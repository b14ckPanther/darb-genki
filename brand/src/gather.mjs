// The Darb Genki mark as flat geometry: the gathered sphere and the threads that rise into it from every
// service. Shared by the SVG marks; src/render.py builds the 3D scene from the same tokens.gather numbers.
// Units: a 200 x 200 box, y down.

/** The mark's parts in the 200 box: the sphere (cx, cy, r), the service points and the threads. */
export function gatherParts(A, { r = 40, cy = 64, base = 160, spread = 92, rise = 30 } = {}) {
  const n = A.services, [s0, s1] = A.spread
  const core = { cx: 100, cy, r }
  const services = Array.from({ length: n }, (_, i) => {
    const a = Math.PI * (s0 + ((s1 - s0) * i) / (n - 1))
    const x = 100 + Math.cos(a) * spread, y = base - Math.sin(a) * 6
    const dx = x - core.cx, dy = y - core.cy, l = Math.hypot(dx, dy)
    const top = [core.cx + (dx / l) * r, core.cy + (dy / l) * r]
    const mid = [(x + top[0]) / 2, (y + top[1]) / 2 - rise * 0.3]
    return { at: [x, y], thread: `M${x.toFixed(2)} ${y.toFixed(2)}Q${mid[0].toFixed(2)} ${mid[1].toFixed(2)} ${top[0].toFixed(2)} ${top[1].toFixed(2)}` }
  })
  // the ground the services stand on: a shallow arc through their feet
  const ground = `M${100 - spread - 6} ${base + 1}Q100 ${base - 13} ${100 + spread + 6} ${base + 1}`
  return { core, services, ground }
}
