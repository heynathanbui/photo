# Nathan Bui — Photography

Client-facing photo portfolio (Scenery / People / Events). Plain HTML/CSS/JS, no build tools beyond Python.

- Edit copy in `template.html`, styles in `assets/css/site.css`.
- Add a photo: put `name.jpg` (1800px long edge) and `name-sm.jpg` (800px) in `assets/img`, add a line to the list in `build.py`, then run `python3 build.py` to regenerate `index.html`.
- Bump `?v=` on the CSS/JS links after edits so browsers pick up changes.

## Albums
Each album in `ALBUMS` (build.py) gets its own page at `albums/<slug>/` built from `album.html`. Its `theme` picks the look and motion in `assets/css/album.css` + `assets/js/album.js` (horizon, skyline, ink, lantern, blinds, contact, arches, album, route, terminal, curtain, ricepaper, spotlight). The home page shows them as cards above each section's grid.
