# goosengames.com

Static site, no build step — the repo root *is* the site. Deployed on Cloudflare Pages.

```
index.html                    landing page: logo, game link, versions link
logo.svg                      the mark (also the favicon), rounded in the SVG itself
_headers                      Cloudflare response headers
_redirects                    Cloudflare redirects (old v01/v02 archive URLs)
.nojekyll                     stops GitHub Pages running Jekyll, if it ever moves
samegreattaste/
  index.html                  /samegreattaste — the build marked playable
  versions.tsv                manifest: id, date, status, note
  v3/index.html               /samegreattaste/v3
  v4/index.html               /samegreattaste/v4
  versions/index.html         /samegreattaste/versions — generated listing
tools/
  release.py                  archives a build and rebuilds the listing
```

## Versioned builds

Every build that has shipped keeps its own permanent address, so an old one
stays playable after the live one moves on.

**Version ids track the game's own save format.** A build whose `CFG.saveKey` is
`sgt_save_v4` is archived as `v4`. All versions share one origin and therefore
one `localStorage`, so this is what stops two archives reading each other's
saved state — `release.py` warns if an id and a save key disagree.

**`/samegreattaste` serves the build marked `playable`, which is not always the
newest.** v4 is further along but unfinished, so v3 is what a visitor gets; v4
is opt-in at its own URL, badged `beta`. To change which build is served, copy
it over `samegreattaste/index.html` and run `--relist` — the listing works out
what is being served by comparing bytes, so it cannot fall out of sync.

Snapshots are byte-identical copies and are not edited afterwards, so an
archived build behaves exactly as it did the day it shipped.

**Archiving a build:**

```bash
python3 tools/release.py --id v5 --status beta --note "Adds the closing-time ending"
```

That copies `samegreattaste/index.html` into `v5/`, appends a row to
`versions.tsv`, and rebuilds the listing. Add `--from <path>` to archive some
other file instead of the live one — that is how an older build gets imported:

```bash
python3 tools/release.py --id v2 --from ~/Downloads/sgt-old.html \
  --note "No sound, no transitions."
```

**After editing notes or statuses in `versions.tsv`**, rebuild the listing
without taking a snapshot:

```bash
python3 tools/release.py --relist
```

## Local preview

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000 — use a server rather than opening the files
directly, so the root-absolute `/logo.svg` paths resolve.
