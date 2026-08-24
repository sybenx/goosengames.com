# goosengames.com

Static site. No build step — the repo root *is* the site.

```
index.html            # landing page: logo, centered, nothing else
logo.svg              # ← drop your logo here (or logo.png + edit the two refs in index.html)
_headers              # Cloudflare Pages response headers (GitHub Pages ignores it)
.nojekyll             # tells GitHub Pages not to run Jekyll
samegreattaste/
  index.html          # served at /samegreattaste  ← replace with your files
```

## Adding the logo

Save the artwork as `logo.svg` in the repo root. `index.html` references it twice:
once as the `<img>` and once as the favicon. If you use a PNG instead, change both
`/logo.svg` refs to `/logo.png` and drop the `type="image/svg+xml"` on the `<link>`.

Size is `min(44vmin, 340px)` — adjust `.logo` in `index.html` to taste.

## Adding pages

Any folder with an `index.html` becomes a clean URL:
`samegreattaste/index.html` → `/samegreattaste`. Both hosts do this automatically.

## Local preview

```
python3 -m http.server 8000
```

Then open http://localhost:8000 — use a server rather than opening the file
directly, so the root-absolute `/logo.svg` paths resolve.
