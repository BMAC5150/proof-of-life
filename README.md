# Proof of Life — Advance Review Copy

A static review site for the novel *Proof of Life*. Pure HTML/CSS/JS, no build step.

## Structure

```
.
├── index.html               # Landing (cover + directory)
├── overview.html            # Premise / reviewer notes
├── chapters/
│   ├── chapter-1.html       # Hell's Kitchen, NYC · 07:40 EST
│   ├── chapter-1a.html      # Croton-on-Hudson, NY · 09:08 EST
│   └── chapter-2.html       # Mott Street, Chinatown, NYC · 09:30 EST
├── css/
│   └── style.css            # All styles (V1 console aesthetic)
└── js/
    └── main.js              # Index dropdown + chapter drawer toggle
```

## Local preview

Just open `index.html` in a browser, or serve the directory with any static server:

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

## Design system (V1 — console / lined ledger)

- **Header strip** — 40px tall, green LED + `PROOF_OF_LIFE / SCOPE` mono label, `INDEX [+] / CLOSE [×]` toggle.
- **Directory dropdown** — full-width listing with status pills: READ / UNREAD / OPEN / CURRENT.
- **Chapter slug** — case-file metadata (CH., LOC., TIME) above the body.
- **Lifted opening** — wrap the first clause of each chapter in `<span class="lift">…</span>`.
- **Log-line footer** — `SYS::ARC.READER … vN.N` and `UPLINK ……… OK` on every page.

Fonts via Google Fonts: Inter Tight, JetBrains Mono, Source Serif 4.
