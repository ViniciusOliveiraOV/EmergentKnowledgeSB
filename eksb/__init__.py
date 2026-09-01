"""EKSB — keep decisions, ideas and sources connected, in plain Markdown."""

import sys

__version__ = "0.1.0a1"


def use_utf8() -> None:
    """Speak UTF-8 on stdin/stdout/stderr, whatever the platform thinks.

    On Windows a *piped* stdout gets the ANSI code page, not UTF-8, so
    `eksb attention > file.txt` wrote cp1252 and anything reading it back as
    UTF-8 saw mojibake — while `->` and other characters the code page has no
    room for degraded to `?`. Interactive Windows consoles are already UTF-8,
    so this changes nothing there.

    One place, called once per run, instead of an `.encode()` at every print.
    Streams that cannot be reconfigured (a StringIO, a detached or replaced
    stdout) are left exactly as they are.
    """
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except (ValueError, OSError, AttributeError):
            pass
