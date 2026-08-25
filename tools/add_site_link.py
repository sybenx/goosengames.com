#!/usr/bin/env python3
"""Append a link back to the site into a build of the game.

  python3 tools/add_site_link.py samegreattaste/index.html [more...]

Shown on the title screen only. The game's action bar is fixed to the bottom
of the screen during the main loop, so a corner link there would sit on top of
the primary button — on a narrow screen it would cover it. `body:has(.title-screen)`
scopes the link to the one screen that has no action bar, with no JavaScript
and no hook into the game's own rendering.

Colours come from the game's own per-act custom properties, so the link follows
the theme through all three acts instead of fighting it.

Idempotent: running it twice changes nothing.
"""
import sys
from pathlib import Path

MARKER = "gg-sitelink"

SNIPPET = """
<!-- Appended by tools/add_site_link.py — not part of the original build.
     A way back to the site, on the title screen only. -->
<style>
  .gg-sitelink{display:none}
  body:has(.title-screen) .gg-sitelink{
    display:block;
    position:fixed;
    right:max(16px, env(safe-area-inset-right));
    bottom:max(16px, env(safe-area-inset-bottom));
    z-index:45;
    font:400 .78rem/1 var(--font-body);
    color:var(--ink2);
    text-decoration:none;
    opacity:.75;
    border-bottom:1px solid currentColor;
    padding-bottom:.15em;
    transition:opacity .18s ease, color .18s ease;
  }
  body:has(.title-screen) .gg-sitelink:hover,
  body:has(.title-screen) .gg-sitelink:focus-visible{opacity:1;color:var(--accent)}
</style>
<a class="gg-sitelink" href="/samegreattaste/versions">other versions</a>
</body>"""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        p = Path(arg)
        s = p.read_text()
        if MARKER in s:
            print(f"  {p}: already has the link, left alone")
            continue
        if s.count("</body>") != 1:
            sys.exit(f"{p}: expected exactly one </body>")
        p.write_text(s.replace("</body>", SNIPPET.lstrip("\n")))
        print(f"  {p}: link added")


if __name__ == "__main__":
    main()
