// Builds every Darb Genki brand asset from src/tokens.json and src/gather.mjs.
//   npm run build              renders the masters in Blender (on PATH, or BLENDER=/path), then cuts everything
//   RENDER=0 npm run build     reuses masters/ and only rebuilds the flat assets
import { execFileSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import opentype from 'opentype.js'
import pngToIco from 'png-to-ico'
import sharp from 'sharp'
import { gatherParts } from '../src/gather.mjs'

const ROOT = fileURLToPath(new URL('..', import.meta.url))
const OUT = `${ROOT}exports/`
const MASTERS = `${ROOT}masters/`
const T = JSON.parse(await readFile(`${ROOT}src/tokens.json`, 'utf8'))
const C = Object.fromEntries(Object.entries(T.color).map(([k, v]) => [k, v.hex]))
const A = T.gather
for (const d of ['icons', 'svg', 'social']) await mkdir(`${OUT}${d}`, { recursive: true })
await mkdir(MASTERS, { recursive: true })

const font = async (f) => opentype.parse((await readFile(`${ROOT}fonts/${f}`)).buffer)
const seal = await font(T.type.seal.file)
const display = await font(T.type.display.file)
const ui = await font(T.type.ui.file)

// ---------- 3D masters (Blender Cycles) ----------

const tileMaster = `${MASTERS}tile.png`, safeMaster = `${MASTERS}safe.png`, heroMaster = `${MASTERS}hero.png`
if (process.env.RENDER !== '0' || ![tileMaster, safeMaster, heroMaster].every(existsSync)) {
  const blender = process.env.BLENDER || 'blender'
  const run = (variant, out, w, h, samples) => {
    console.log(`rendering ${variant} ${w}x${h} at ${samples} samples`)
    execFileSync(blender, ['-b', '-P', `${ROOT}src/render.py`, '--', variant, out, String(w), String(h), String(samples)], { stdio: ['ignore', 'ignore', 'inherit'] })
  }
  run('tile', tileMaster, 2048, 2048, T.render.samples.icon)
  run('safe', safeMaster, 2048, 2048, T.render.samples.icon)
  run('hero', heroMaster, T.icons.hero[0], T.icons.hero[1], T.render.samples.hero)
}

// ---------- the flat marks: the same sphere and threads as the render ----------

/** The gathered sphere: `halo` behind it, threads rising from every service point. */
function gatherSvg({ fill, halo, thread, node, threadW = 2.2, nodeR = 3.6, count = A.services, geo = {}, groundW = threadW * 0.9 }) {
  const P = gatherParts({ ...A, services: count }, geo), { cx, cy, r } = P.core
  const glow = halo ? `<circle cx="${cx}" cy="${cy}" r="${r * 1.55}" fill="url(#h)"/>` : ''
  const threads = P.services.map((s) => `<path d="${s.thread}" fill="none" stroke="${thread}" stroke-width="${threadW}" stroke-linecap="round"/>`).join('')
  const nodes = P.services.map((s) => `<circle cx="${s.at[0].toFixed(2)}" cy="${s.at[1].toFixed(2)}" r="${nodeR}" fill="${node}"/>`).join('')
  const ground = groundW ? `<path d="${P.ground}" fill="none" stroke="${node}" stroke-width="${groundW}" stroke-linecap="round" opacity=".55"/>` : ''
  return `${glow}${ground}${threads}${nodes}<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}"/>`
}
const defs = `<radialGradient id="l" cx="50%" cy="34%" r="75%"><stop offset="0" stop-color="${C.forest}"/><stop offset="1" stop-color="${C.night}"/></radialGradient>
  <radialGradient id="h"><stop offset=".55" stop-color="${C.gold}" stop-opacity=".75"/><stop offset="1" stop-color="${C.gold}" stop-opacity="0"/></radialGradient>
  <radialGradient id="c" cx="42%" cy="38%" r="65%"><stop offset="0" stop-color="#FFF8E6"/><stop offset=".7" stop-color="${C.goldLight}"/><stop offset="1" stop-color="${C.gold}"/></radialGradient>`
const svg = (body) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><defs>${defs}</defs>${body}</svg>\n`
const tile = `<rect width="200" height="200" rx="44" fill="url(#l)"/>`

const svgs = {
  'mark-on-night.svg': svg(`${tile}${gatherSvg({ fill: 'url(#c)', halo: true, thread: C.gold, node: C.goldLight })}`),
  'mark-gold.svg': svg(gatherSvg({ fill: C.gold, thread: C.gold, node: C.gold, threadW: 3, nodeR: 4.5, count: 9, geo: { r: 46, cy: 58, base: 176, spread: 92 } })),
  'mark-ivory.svg': svg(gatherSvg({ fill: C.ivory, thread: C.ivory, node: C.ivory, threadW: 3, nodeR: 4.5, count: 9, geo: { r: 46, cy: 58, base: 176, spread: 92 } })),
  'mark-ink.svg': svg(gatherSvg({ fill: C.ink, thread: C.ink, node: C.ink, threadW: 3, nodeR: 4.5, count: 9, geo: { r: 46, cy: 58, base: 176, spread: 92 } })),
  // small sizes: five heavy threads and a big sphere, so it reads at 16 px
  'favicon.svg': svg(`<rect width="200" height="200" rx="44" fill="${C.night}"/>${gatherSvg({ fill: C.goldLight, thread: C.gold, node: C.gold, count: 5, threadW: 12, nodeR: 12, groundW: 0, geo: { r: 56, cy: 70, base: 168, spread: 76 } })}`),
  'badge-mono.svg': svg(gatherSvg({ fill: '#fff', thread: '#fff', node: '#fff', count: 5, threadW: 12, nodeR: 12, groundW: 0, geo: { r: 58, cy: 68, base: 172, spread: 80 } })),
}
for (const [f, s] of Object.entries(svgs)) await writeFile(`${OUT}svg/${f}`, s)

// ---------- wordmark (text outlined: no font needed to display it) ----------

const outline = (f, text, x, y, size, fill) => f.getPath(text, x, y, size).toSVG(2).replace('<path ', `<path fill="${fill}" `)
function lockup(ink, sub, accent) {
  const NAME = 196, DARB = 50, JP = 40, GAP = 26
  const nameB = display.getPath(T.shortName, 0, 0, NAME).getBoundingBox()
  const darbB = ui.getPath('Darb', 0, 0, DARB).getBoundingBox()
  const jpB = seal.getPath(T.japanese, 0, 0, JP).getBoundingBox()
  const base = -(nameB.y1 - GAP + darbB.y1)
  const H = base + Math.max(nameB.y2, 0)
  const x0 = H + 60
  const jpX = x0 + (nameB.x2 - nameB.x1) + 36 - jpB.x1
  const W = jpX + jpB.x2 + 4
  const mark = svgs['mark-on-night.svg'].replace(/<\/?svg[^>]*>/g, '').replace('id="h"', 'id="wh"').replaceAll('url(#h)', 'url(#wh)').replace('id="c"', 'id="wc"').replaceAll('url(#c)', 'url(#wc)').replace('id="l"', 'id="wl"').replaceAll('url(#l)', 'url(#wl)')
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -8 ${Math.ceil(W)} ${Math.ceil(H + 16)}">
  <g transform="scale(${H / 200})">${mark}</g>
  ${outline(ui, 'Darb', x0 + 6 - darbB.x1, base + nameB.y1 - GAP, DARB, sub)}
  ${outline(display, T.shortName, x0 - nameB.x1, base, NAME, ink)}
  ${outline(seal, T.japanese, jpX, base, JP, accent)}
</svg>
`
}
await writeFile(`${OUT}svg/wordmark-on-dark.svg`, lockup(C.ivory, C.muted, C.gold))
await writeFile(`${OUT}svg/wordmark-on-light.svg`, lockup(C.ink, '#6f6357', C.goldDeep))

// ---------- icon set: the cast medallion on the night tile ----------

/** iOS-style superellipse ("squircle"), n = 5. */
function squircle(size, fill = '#fff') {
  const r = size / 2, pts = []
  for (let i = 0; i < 360; i++) {
    const t = (i / 360) * Math.PI * 2, c = Math.cos(t), s = Math.sin(t)
    pts.push(`${(r + Math.sign(c) * Math.abs(c) ** 0.4 * r).toFixed(2)},${(r + Math.sign(s) * Math.abs(s) ** 0.4 * r).toFixed(2)}`)
  }
  return Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}"><polygon points="${pts.join(' ')}" fill="${fill}"/></svg>`)
}
const resized = (src, size) => sharp(src).resize(size, size, { kernel: 'lanczos3' }).png().toBuffer()
const cut = async (buf, size) => sharp(buf).composite([{ input: squircle(size), blend: 'dest-in' }]).png()

for (const s of T.icons.tile) await (await cut(await resized(tileMaster, s), s)).toFile(`${OUT}icons/icon-${s}.png`)
for (const s of T.icons.maskable) await sharp(await resized(safeMaster, s)).toFile(`${OUT}icons/icon-maskable-${s}.png`)
await sharp(await resized(tileMaster, T.icons.apple)).flatten({ background: C.night }).toFile(`${OUT}icons/apple-touch-icon.png`)
{
  // macOS / desktop: 824 px squircle on a 1024 canvas with the system drop shadow
  const size = T.icons.mac, body = Math.round(size * 0.805), off = Math.round((size - body) / 2)
  const art = await (await cut(await resized(tileMaster, body), body)).toBuffer()
  const shadow = await sharp({ create: { width: size, height: size, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } } })
    .composite([{ input: squircle(body, 'rgba(0,0,0,0.55)'), left: off, top: off + Math.round(size * 0.012) }])
    .blur(size * 0.012).png().toBuffer()
  await sharp(shadow).composite([{ input: art, left: off, top: off }]).png().toFile(`${OUT}icons/icon-desktop-${size}.png`)
}
for (const s of T.icons.favicon) await sharp(Buffer.from(svgs['favicon.svg'])).resize(s, s).png().toFile(`${OUT}icons/favicon-${s}.png`)
await writeFile(`${OUT}icons/favicon.ico`, await pngToIco(T.icons.favicon.map((s) => `${OUT}icons/favicon-${s}.png`)))
await sharp(Buffer.from(svgs['badge-mono.svg'])).resize(T.icons.badge, T.icons.badge).png().toFile(`${OUT}icons/badge-${T.icons.badge}.png`)
await writeFile(`${OUT}icons/favicon.svg`, svgs['favicon.svg'])

// ---------- social: the hero render with the copy set on its quiet left side ----------

/** Wraps `text` to lines no wider than `max` at `size` in font `f`. */
function wrap(f, text, size, max) {
  const lines = [''], words = text.split(' ')
  for (const w of words) {
    const next = lines.at(-1) ? `${lines.at(-1)} ${w}` : w
    if (f.getAdvanceWidth(next, size) > max && lines.at(-1)) lines.push(w)
    else lines[lines.length - 1] = next
  }
  return lines
}
async function social(w, h, file) {
  const u = h / 630, x = 72 * u
  const shade = `<linearGradient id="s" x1="0" x2="1"><stop offset="0" stop-color="${C.night}" stop-opacity=".85"/><stop offset=".55" stop-color="${C.night}" stop-opacity="0"/></linearGradient>`
  const nameSize = 112 * u, nameY = 300 * u
  const desc = wrap(ui, T.description, 22 * u, 540 * u)
  const copy = [
    outline(ui, 'Darb', x + 4 * u, 196 * u, 34 * u, C.muted),
    outline(display, T.shortName, x, nameY, nameSize, C.ivory),
    outline(seal, T.japanese, x + display.getAdvanceWidth(T.shortName, nameSize) + 22 * u, nameY, 34 * u, C.gold),
    outline(ui, T.tagline, x + 2 * u, 372 * u, 34 * u, C.gold),
    ...desc.map((l, i) => outline(ui, l, x + 2 * u, (428 + i * 32) * u, 22 * u, C.muted)),
  ].join('')
  const over = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><defs>${shade}</defs><rect width="${w}" height="${h}" fill="url(#s)"/>${copy}</svg>`)
  await sharp(heroMaster).resize(w, h, { kernel: 'lanczos3' }).composite([{ input: over }]).png().toFile(file)
}
await social(T.icons.og[0], T.icons.og[1], `${OUT}social/og-image.png`)
await social(T.icons.hero[0], T.icons.hero[1], `${OUT}social/hero.png`)

// ---------- manifest, tokens, head tags ----------

const manifest = {
  name: T.name,
  short_name: T.shortName,
  description: T.tagline,
  display: 'standalone',
  background_color: C.night,
  theme_color: C.night,
  icons: [
    ...T.icons.tile.map((s) => ({ src: `/icons/icon-${s}.png`, sizes: `${s}x${s}`, type: 'image/png', purpose: 'any' })),
    ...T.icons.maskable.map((s) => ({ src: `/icons/icon-maskable-${s}.png`, sizes: `${s}x${s}`, type: 'image/png', purpose: 'maskable' })),
    { src: `/icons/badge-${T.icons.badge}.png`, sizes: `${T.icons.badge}x${T.icons.badge}`, type: 'image/png', purpose: 'monochrome' },
  ],
}
await writeFile(`${OUT}manifest.webmanifest`, JSON.stringify(manifest, null, 2) + '\n')

await writeFile(`${OUT}tokens.css`, `/* Generated from src/tokens.json by scripts/build.mjs. Edit the JSON, not this file. */
:root {
${Object.entries(T.color).map(([k, v]) => `  --${k.replace(/[A-Z]/g, (m) => '-' + m.toLowerCase())}: ${v.hex}; /* ${v.role} */`).join('\n')}
  --font-seal: '${T.type.seal.family}', 'Hiragino Mincho ProN', serif;
  --font-display: '${T.type.display.family}', 'Hiragino Mincho ProN', serif;
  --font-ui: '${T.type.ui.family}', system-ui, sans-serif;
}
`)

await writeFile(`${OUT}head.html`, `<link rel="icon" href="/icons/favicon.ico" sizes="48x48">
<link rel="icon" href="/icons/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="${C.night}">
<meta property="og:title" content="${T.name}">
<meta property="og:description" content="${T.tagline}">
<meta property="og:image" content="/social/og-image.png">
<meta name="twitter:card" content="summary_large_image">
`)
console.log('built', OUT)
