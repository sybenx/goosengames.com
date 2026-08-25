# goosengames.com

Static site, no build step — the repo root *is* the site. Deployed on Cloudflare Pages.

```
index.html                    landing page: logo, centered, nothing else
logo.svg                      the mark (also the favicon)
_headers                      Cloudflare response headers
.nojekyll                     stops GitHub Pages running Jekyll, if it ever moves
samegreattaste/
  index.html                  /samegreattaste — the current build
  versions.tsv                version manifest (id, date, note)
  v01/index.html              /samegreattaste/v01 — frozen snapshot
  versions/index.html         /samegreattaste/versions — generated listing
tools/
  release.py                  snapshots the current build as the next vNN
```

## Versioned builds

`/samegreattaste` always serves the newest build. Every build that has shipped
also keeps its own permanent address — `/samegreattaste/v01`, `/samegreattaste/v02`
— so an old one stays playable after the live one moves on.

Snapshots are byte-identical copies and are never edited afterwards, so an
archived build behaves exactly as it did the day it shipped.

**Shipping an update:** edit `samegreattaste/index.html` as usual, then freeze
what you just replaced *before* you overwrite it — or, more simply, snapshot the
new build right after you finish it:

```bash
python3 tools/release.py --note "Adds act 4 and the closing-time ending"
```

That copies `samegreattaste/index.html` to the next unused `vNN/`, appends a row
to `versions.tsv`, and rebuilds the listing page.

**Importing an older build** that predates this setup:

```bash
python3 tools/release.py --id v00 --from ~/Downloads/sgt-old.html --note "No sound, no transitions."
```

**After only editing notes in `versions.tsv`**, rebuild the listing without
taking a snapshot:

```bash
python3 tools/release.py --relist
```

### One caveat: saves are shared

All versions run on the same origin, so they share one `localStorage`. The game
already namespaces its keys (`sgt_save_v4`, `sgt_audio_v1`) — keep bumping the
number in `CFG.saveKey` whenever the save format changes, or a v01 save will be
read by v02 and misinterpreted.

## Local preview

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000 — use a server rather than opening the files
directly, so the root-absolute `/logo.svg` paths resolve.
