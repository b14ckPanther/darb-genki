# Darb Genki brand

Genki is a Darb product. It wears Darb's colours (night, forest, gold, ivory) and has its own mark: **every service raises one thread of light, and they all rise into a single glowing sphere.** In the show, the Genki-dama (元気玉, the Spirit Bomb) is energy lent by everyone who raises their hands. Darb Genki gathers telemetry lent by every service into one view.

The hero image is the product's own signature, the Mesh Map: services as places, calls as roads, each request a point of light on its way, and one road turned amber because it got slow.

Chosen by Nour from four meaning-led directions (A "Lend Your Light" for the icon, B "The Mesh Map" for the hero; C "One Thread Through All" and D "Broken on Purpose" are kept in `concepts/`).

## See it

```sh
cd brand && npm install
node scripts/serve.mjs          # http://127.0.0.1:4180/ : brand sheet with every asset
```

## Rebuild every asset

```sh
npm run build                   # renders the three masters in Blender Cycles, then cuts everything
RENDER=0 npm run build          # reuses masters/ (no Blender needed) and rebuilds the flat assets
BLENDER=/path/to/blender npm run build   # when blender is not on PATH
```

Nothing is drawn by hand and nothing is hardcoded in the build:

| File | Holds |
|---|---|
| `src/tokens.json` | colours and roles (gold healthy, amber slow, seal red broken), type, the gathered sphere (service count, spread, camera), the Mesh Map (places, roads, which road is slow), render samples, icon sizes, copy |
| `src/gather.mjs` | the sphere, threads and ground for the flat SVG marks, from the same `tokens.gather` numbers the render uses |
| `src/render.py` | Blender scenes: the gathered sphere (`tile`, and `safe` with room for maskable icons) and the Mesh Map (`hero`) |
| `scripts/build.mjs` | renders the masters, cuts every icon, writes the SVG marks, wordmarks, social cards, manifest and CSS tokens |
| `masters/` | the three Blender renders, committed so the flat assets rebuild without Blender |
| `concepts/` | the four directions and `blender/genki.py`, the script that rendered them |

## What's in `exports/`

| Path | Use |
|---|---|
| `icons/icon-192.png`, `icon-512.png` | PWA icons, purpose `any` (squircle cut) |
| `icons/icon-maskable-192.png`, `-512.png` | PWA maskable (sphere and threads inside the 80% safe zone) |
| `icons/apple-touch-icon.png` | iOS home screen, 180 px, opaque |
| `icons/icon-desktop-1024.png` | Desktop: macOS grid, 824 px body with system shadow |
| `icons/favicon.ico`, `favicon.svg`, `favicon-16/32/48.png` | Browser tab: five heavy threads and a big sphere, so it reads at 16 px |
| `icons/badge-96.png` | Notification badge and Android monochrome icon |
| `svg/mark-on-night.svg` | The flat mark on its night tile, with its halo |
| `svg/mark-gold.svg`, `mark-ivory.svg`, `mark-ink.svg` | The mark alone, for any background |
| `svg/wordmark-on-dark.svg`, `-on-light.svg` | Lockup: mark, Darb, Genki, 元気 (text outlined, no font needed) |
| `social/og-image.png`, `social/hero.png` | 1200 x 630 sharing card and 2400 x 1260 README hero |
| `manifest.webmanifest`, `head.html`, `tokens.css` | Drop-in PWA manifest, `<head>` tags and CSS tokens |

## Rules

- Gold means healthy, amber means slow (over its latency objective), seal red means broken or a chaos drill running. Never use them as decoration, and never show colour as the only signal.
- Threads always rise into the sphere: every service gives, the view gathers. The sphere is never drawn without the services under it.
- No generic "network" art: no glowing node clouds, circuit boards or isometric server racks.
- Darb's doorway outline belongs to Darb itself; Genki never uses it.
- Every visual is original and made in code. No official Dragon Ball art, logos, characters or audio.
- Fonts: Zen Antique (display), Geist (interface) and Yuji Boku (元気 only), all under the SIL Open Font License (`fonts/`).
