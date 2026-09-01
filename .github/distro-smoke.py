"""Install-and-use smoke test, run inside a Linux distribution container.

Deliberately much smaller than the main suite: it proves EKSB installs and
works on this libc, this Python and this filesystem — not that every
behaviour is correct, which the Ubuntu/Windows/macOS matrix already covers.

Written in Python rather than shell because the assertions are filesystem
and text questions, and every distro here has the product's own runtime
installed by definition. `ls | wc -l` does not mean the same thing on
BSD, busybox and GNU; `pathlib.glob` does.
"""
import os
import pathlib
import platform
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(tempfile.mkdtemp(prefix="eksb-smoke-"))
ENV = dict(os.environ, EKSB_CONFIG_DIR=str(ROOT / "config"), NO_COLOR="1")


def eksb(*args, expect=0):
    """Run the command as a user would, with stdout piped — so this also
    exercises the non-interactive path on every distro."""
    r = subprocess.run([sys.executable, "-m", "eksb", *args],
                       capture_output=True, text=True, env=ENV)
    print(f"$ eksb {' '.join(args)}", flush=True)
    print(r.stdout + r.stderr, flush=True)
    if r.returncode != expect:
        raise SystemExit(f"eksb {' '.join(args)} exited {r.returncode}, "
                         f"expected {expect}")
    return r.stdout


def main() -> int:
    print(f"python  {sys.version}")
    print(f"platform {platform.platform()}")
    print(f"libc    {platform.libc_ver()}")     # ('glibc', '2.x') or ('', '') on musl
    print(f"fs      {ROOT}", flush=True)

    eksb("--version")

    # the demo: bundled data, package_data, and a read path
    demo = ROOT / "demo"
    eksb("demo", str(demo))
    assert (demo / "_system" / "workspace.yml").is_file(), "demo not installed"
    out = eksb("search", "partitioning", "-w", str(demo))
    assert "Time-Range Partitioning" in out, out
    assert "Open result" not in out, "prompted on a pipe"
    eksb("validate", str(demo))

    # accented output must survive whatever this distro thinks the locale is
    out = eksb("--lang", "pt-BR", "attention", "-w", str(demo))
    assert "Coisas que precisam da sua atenção" in out, out
    assert "�" not in out, out

    # a workspace of one's own
    mine = ROOT / "Meu Espaço ✓"                # spaces and non-ASCII on this fs
    eksb("init", str(mine))
    assert (mine / "concepts").is_dir(), "scaffold missing"

    # ingest a small project
    proj = ROOT / "proj"
    (proj / "docs").mkdir(parents=True)
    (proj / "README.md").write_text("# Atlas\n\nRead latency is the constraint.\n",
                                    encoding="utf-8")
    (proj / "docs" / "d.md").write_text("# Decisions\n\nAdopted partitioning.\n",
                                        encoding="utf-8")
    (proj / "main.py").write_text("print(1)\n", encoding="utf-8")
    out = eksb("ingest", str(proj), "--name", "Atlas", "-w", str(mine))
    assert "Atlas" in out, out

    sources = list((mine / "_sources").glob("*.md"))
    assert len(sources) == 2, [p.name for p in sources]   # the two .md, not main.py

    out = eksb("search", "latency", "-w", str(mine))
    assert "Atlas" in out, out
    eksb("validate", str(mine))
    assert "indexed" in eksb("projects", "-w", str(mine))

    print("\nsmoke ok", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
