"""
Encoding for the process's own output streams.

Every file this project reads or writes names its encoding explicitly. The
output streams were the exception: on Windows they default to the locale ANSI
codepage — cp1252 on a stock install — which has no mapping for any Indic
script. Printing a Marathi question raises UnicodeEncodeError, and because the
retrieval eval is this project's only regression gate, a reporting detail
became a non-zero exit.

Setting PYTHONIOENCODING=utf-8 avoids it, but a gate that passes only when the
caller remembers an environment variable is not a gate. Entry points that can
print corpus, lexicon or user-submitted text call use_utf8_output() instead.
"""

from __future__ import annotations

import sys


def use_utf8_output() -> None:
    """
    Re-encode stdout and stderr as UTF-8 for the rest of the process.

    UTF-8, rather than errors="replace" over the existing codepage, because the
    two differ exactly where it matters. Replacement mangles Devanagari to
    question marks unconditionally, including when output is redirected to a
    file or captured by CI — destinations that would have carried the bytes
    intact. Re-encoding keeps the text readable wherever the destination can
    render it, and costs mojibake only on a legacy console that could never
    have shown the script anyway.

    errors="replace" is still set, as a backstop rather than a strategy: it
    makes an unencodable character a visible artefact instead of an exception,
    so no future output path can turn a diagnostic line into a failed exit
    code.

    stderr is included deliberately. An exception carrying a lexicon term in
    its message would otherwise raise a second UnicodeEncodeError while its
    traceback was being written, replacing the real error with this one.
    """
    for stream in (sys.stdout, sys.stderr):
        # A stream replaced by a test runner or capture harness need not be a
        # TextIOWrapper, and one already detached raises. In both cases the
        # encoding is that harness's business, and failing here would be the
        # very crash this function exists to prevent.
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            continue
