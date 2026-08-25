# goosengames.com

Static site, no build step — the repo root *is* the site. Deployed on Cloudflare Pages.

```
index.html                    landing page: logo, game link, versions link
logo.svg                      the mark, rounded in the SVG itself; the SVG favicon
favicon.ico                   16+16/32 fallback for browsers without SVG favicons
apple-touch-icon.png          180px, square — iOS applies its own rounding
icon-192.png icon-512.png     Android / web manifest
site.webmanifest              name, colours and icons for Add to Home Screen
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

## Icons

`logo.svg` is rounded in the file, which is right for a browser tab but wrong
for a home screen: iOS and Android apply their own mask, and a pre-rounded
icon gets rounded twice with the background showing through at the corners.
So the raster icons are generated from a **square, unrounded** copy with an
explicit opaque backing — iOS also flattens any transparency to black.

The archived game pages carry no icon tags of their own and must not be edited.
They are covered anyway: browsers fall back to `/favicon.ico` and iOS falls
back to `/apple-touch-icon.png` at the site root when a page declares neither.
The manifest is *not* auto-discovered that way, so an Android home-screen save
made from a game page uses the favicon rather than the 512px icon.

Regenerating them needs a rasteriser. There is none in this repo; they were
built with macOS `qlmanage` plus `sips`, and `favicon.ico` was assembled by
hand as an ICO wrapping two PNGs. Note `qlmanage` flattens alpha to white, so
it is only safe for the square icons, which are opaque by construction.

## If an asset serves the wrong thing

Cloudflare's edge cache is separate from Pages, and a new deployment does not
purge it. If a request arrives for a file that is not deployed yet, Pages
answers 200 with HTML, and `_headers` then caches *that* under the asset's URL
for its full lifetime — a new deploy will not dislodge it.

To tell an edge problem from an origin one, add a query string. It changes the
cache key, so the response comes from the origin:

```bash
curl -sI https://goosengames.com/logo.svg          # what visitors get
curl -sI https://goosengames.com/logo.svg?cb=1     # what is actually deployed
```

If those disagree, the deployment is fine and the cache is stale. Fix it in the
Cloudflare dashboard under Caching → Configuration → Purge Cache, purging that
one URL. Nothing in this repo can clear it.

## Local preview

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000 — use a server rather than opening the files
directly, so the root-absolute `/logo.svg` paths resolve.
