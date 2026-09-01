# Linux distribution smoke matrix

The main CI matrix answers *does EKSB behave correctly* — 105 tests on
Ubuntu, Windows and macOS across Python 3.11–3.13. This one answers a
narrower question: **does it install and work on a distribution that is not
Ubuntu**, with that distribution's own Python and its own libc.

It is deliberately small. Install, demo, search, validate, create a
workspace, ingest a project, search it, validate it. If a distro breaks, it
breaks here first and the job name says which one.

## What runs

| Distribution | Image | libc |
|---|---|---|
| Debian 12 | `debian:12` | glibc |
| Ubuntu 24.04 | `ubuntu:24.04` | glibc |
| Linux Mint 22 | `linuxmintd/mint22-amd64` | glibc |
| Fedora 41 | `fedora:41` | glibc |
| Rocky Linux 9 | `quay.io/rockylinux/rockylinux:9` | glibc |
| openSUSE Tumbleweed | `opensuse/tumbleweed` | glibc |
| Arch Linux | `archlinux:latest` | glibc |
| Manjaro | `manjarolinux/base` | glibc |
| Void Linux | `ghcr.io/void-linux/void-glibc:latest` | glibc |
| Void Linux | `ghcr.io/void-linux/void-musl:latest` | musl |
| Alpine 3.20 | `alpine:3.20` | musl |

Alpine and Void-musl are the ones that matter most: they are the only
environments here where the C library is not glibc.

## How it runs

The containers run under `docker run` on an Ubuntu runner, not with the
workflow's `container:` key. `actions/checkout` needs a glibc-linked Node,
which Alpine does not have; checking out on the host and mounting the
repository read-only sidesteps that without installing anything into the
distro that a user would not install.

The smoke itself is [`.github/distro-smoke.py`](../../.github/distro-smoke.py) —
Python, not shell, because the assertions are filesystem and text questions
and the product's runtime is installed on every one of these images by
definition. `ls | wc -l` does not mean the same thing on GNU, BSD and
busybox; `pathlib.glob` does.

## Notes on individual distros

- **Manjaro** needs `pacman -Syu`, not `pacman -Sy`. The image ships a glibc
  older than the Python in the repositories, and a partial upgrade installs
  a Python that cannot import `math`. This is the image's own well-known
  constraint, not an EKSB problem.
- **Rocky Linux 9** defaults to Python 3.9, which EKSB does not support, so
  the job installs `python3.11` explicitly — the same thing a user on RHEL 9
  would do.
- **PEP 668** marks the system Python as externally managed on most of these.
  The job passes `--break-system-packages`, falling back to a plain install
  on the older pips that do not know the flag.

## Running one locally

Any container runtime will do:

```sh
podman run --rm -v "$PWD:/src:ro" alpine:3.20 sh -c '
  apk add --no-cache python3 py3-pip
  mkdir -p /work/.github && cd /work
  cp -r /src/eksb /src/pyproject.toml /src/README.md /src/LICENSE /src/VERSION .
  cp /src/.github/distro-smoke.py .github/
  python3 -m pip install --break-system-packages .
  python3 .github/distro-smoke.py
'
```
