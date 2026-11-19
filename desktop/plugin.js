// tvl-studio — desktop half. Loads UNCOMPILED (no JSX): jsx()/jsxs() only.
// The APP is TVL-branded (explicit TVL palette per Lisa's instruction); the
// MEDIA follows the selected brand kit / script. Imports are limited to
// @hermes/plugin-sdk, react, react/jsx-runtime.
import { host, haptic, useValue, Badge, Button, ROUTES_AREA, SIDEBAR_NAV_AREA } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'
import { useState, useEffect, useCallback } from 'react'

const BUILD = '0.1.0 · ui1'
const NAME = 'TVL Studio'

// TVL internal design language (docs/TVL-INTERNAL-DESIGN-LANGUAGE.md).
const T = {
  bg: '#0a0e1a', card: '#0f1524', card2: '#111827', line: '#1f2937',
  cyan: '#22d3ee', violet: '#8b5cf6', green: '#34d399', amber: '#facc15',
  red: '#f87171', text: '#f1f5f9', muted: '#94a3b8',
}
const mono = { fontFamily: "'JetBrains Mono', ui-monospace, monospace" }
const label = { ...mono, fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: T.muted }

const SAMPLE = `CAST: GUIDE — a friendly cyan robot with a rounded head and antenna
CAST: SKEPTIC — a small red stick figure with crossed arms

INT. THE LAB — NIGHT

GUIDE: Every big idea starts as a paper nobody has read yet.
SKEPTIC: And most of them stay that way.
GUIDE: Not when an agent scores it, checks the market, and builds the product.

INT. THE MARKET — DAY

GUIDE: Evidence first. Then we ship.
SKEPTIC: Fine. Show me the numbers.`

function chip(text, color) {
  return jsx('span', {
    style: { ...mono, fontSize: 9, letterSpacing: '0.08em', textTransform: 'uppercase', color, border: `1px solid ${color}55`, borderRadius: 20, padding: '2px 8px', whiteSpace: 'nowrap' },
    children: text,
  })
}

function Stepper({ p }) {
  const steps = [
    ['Script', true],
    ['Images', p.imaged >= p.shots && p.shots > 0],
    ['Voices', p.voiced >= p.shots && p.shots > 0],
    ['Film', Boolean(p.film)],
  ]
  return jsxs('div', { className: 'flex items-center gap-2 flex-wrap', children: steps.map(([name, done], i) =>
    jsxs('div', { className: 'flex items-center gap-2', children: [
      i > 0 ? jsx('div', { style: { width: 22, height: 1, background: T.line } }) : null,
      jsxs('div', { className: 'flex items-center gap-1.5', children: [
        jsx('span', { style: { width: 8, height: 8, borderRadius: 8, background: done ? T.green : T.line, display: 'inline-block' } }),
        jsx('span', { style: { ...mono, fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', color: done ? T.green : T.muted }, children: name }),
      ] }),
    ] }, name)) })
}

function ShotCard({ s, cast }) {
  const state = s.audio ? ['ready', T.green] : s.image ? ['needs voice', T.amber] : ['needs image', T.violet]
  return jsxs('div', {
    style: { background: T.card, border: `1px solid ${T.line}`, borderRadius: 14, overflow: 'hidden' },
    children: [
      jsxs('div', { style: { position: 'relative', aspectRatio: '16/9', background: T.card2 }, children: [
        s.thumb ? jsx('img', { src: s.thumb, alt: '', style: { width: '100%', height: '100%', objectFit: 'cover', display: 'block' } })
          : jsxs('div', { style: { position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 6 }, children: [
              jsx('span', { style: { ...mono, fontSize: 22, color: T.line }, children: s.id.toUpperCase() }),
              jsx('span', { style: { ...label }, children: 'image pending' }),
            ] }),
        jsx('div', { style: { position: 'absolute', top: 8, left: 8 }, children: chip(s.id, T.cyan) }),
        jsx('div', { style: { position: 'absolute', top: 8, right: 8 }, children: chip(state[0], state[1]) }),
      ] }),
      jsxs('div', { className: 'p-3 flex flex-col gap-2', children: [
        jsx('div', { style: { ...label }, children: s.scene }),
        jsx('div', { style: { fontSize: 12.5, color: T.text, lineHeight: 1.4 }, children: s.title }),
        jsxs('div', { className: 'flex flex-col gap-1', children: (s.lines || []).slice(0, 4).map((l, i) =>
          jsxs('div', { style: { fontSize: 11.5, color: T.muted, lineHeight: 1.4 }, children: [
            jsx('span', { style: { ...mono, fontSize: 9.5, color: (cast[l.character] || {}).voice ? T.cyan : T.muted, marginRight: 6 }, children: l.character }),
            l.text.length > 110 ? l.text.slice(0, 109) + '…' : l.text,
          ] }, i)) }),
        s.duration ? jsx('div', { style: { ...mono, fontSize: 10, color: T.muted }, children: `vo ${s.duration}s` }) : null,
      ] }),
    ],
  })
}

function ImportPanel({ ctx, brands, onDone, onClose }) {
  const [name, setName] = useState('')
  const [script, setScript] = useState('')
  const [brand, setBrand] = useState('script-driven')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const submit = async () => {
    if (!name.trim() || !script.trim()) { setErr('A name and a script are both required.'); return }
    setBusy(true); setErr('')
    try {
      const d = await ctx.rest('/import', { method: 'POST', body: { name, script, brand } })
      onDone(d.project.id)
    } catch (e) { setErr(String((e && e.message) || e)) } finally { setBusy(false) }
  }
  const field = { background: T.card2, border: `1px solid ${T.line}`, borderRadius: 9, color: T.text, font: 'inherit', fontSize: 13, padding: '9px 12px', width: '100%' }
  return jsxs('div', { style: { background: T.card, border: `1px solid ${T.line}`, borderRadius: 14, padding: 18 }, className: 'flex flex-col gap-3', children: [
    jsxs('div', { className: 'flex items-center gap-2', children: [
      jsx('div', { style: { fontSize: 14, fontWeight: 600, color: T.text }, children: 'New film — import a script' }),
      jsx('div', { style: { marginLeft: 'auto' }, children: jsx(Button, { variant: 'outline', size: 'xs', onClick: onClose, children: 'Close' }) }),
    ] }),
    jsx('div', { style: { fontSize: 12, color: T.muted, lineHeight: 1.5 }, children: 'Paste a script: CHARACTER: dialogue lines get their own voices, CAST: NAME — description lines lock how characters look, INT./EXT. headings split scenes. Plain prose works too — it becomes narration.' }),
    jsx('input', { style: field, placeholder: 'Film name — e.g. Reading a Score', value: name, onChange: e => setName(e.target.value) }),
    jsx('textarea', { style: { ...field, minHeight: 180, resize: 'vertical', ...mono, fontSize: 12 }, placeholder: 'Paste the script…', value: script, onChange: e => setScript(e.target.value) }),
    jsxs('div', { className: 'flex items-center gap-2 flex-wrap', children: [
      jsx('span', { style: label, children: 'Brand kit' }),
      jsx('select', { style: { ...field, width: 'auto' }, value: brand, onChange: e => setBrand(e.target.value),
        children: brands.map(b => jsx('option', { value: b.id, children: b.name }, b.id)) }),
      jsx(Button, { variant: 'outline', size: 'xs', onClick: () => { setScript(SAMPLE); if (!name) setName('Guide and Skeptic') }, children: 'Use sample script' }),
      jsx('div', { style: { marginLeft: 'auto' }, children: jsx(Button, { size: 'xs', disabled: busy, onClick: submit, style: { background: T.violet, color: '#fff' }, children: busy ? 'Parsing…' : 'Build storyboard' }) }),
    ] }),
    jsx('div', { style: { fontSize: 11, color: T.muted }, children: 'The kit brands the media (image style, palette, voices, music). “Script-driven” leaves visuals to the script. The app itself always wears TVL.' }),
    err ? jsx('div', { style: { fontSize: 12, color: T.red }, children: err }) : null,
  ] })
}

function ProjectView({ ctx, id, brands, onBack }) {
  const [d, setD] = useState(null)
  const [err, setErr] = useState('')
  const [note, setNote] = useState('')
  const load = useCallback(async () => {
    try { setD(await ctx.rest(`/project/${id}`)) } catch (e) { setErr(String((e && e.message) || e)) }
  }, [ctx, id])
  useEffect(() => { void load() }, [load])
  useEffect(() => ctx.setInterval(() => { void load() }, 4000), [ctx, load])

  const act = async (path, okMsg, body) => {
    setErr(''); setNote('')
    try { await ctx.rest(path, { method: 'POST', body: body || {} }); setNote(okMsg); void load() }
    catch (e) { setErr(String((e && e.message) || e)) }
  }
  const sendToAgent = (text) => {
    const ok = host.composer.submit(null, text)
    host.notify({ kind: ok ? 'info' : 'error', message: ok ? 'Handed to the agent in this session.' : 'No active chat composer found — open a session first.' })
  }

  if (!d) return jsx('div', { style: { color: T.muted, fontSize: 13 }, children: err || 'Loading storyboard…' })
  const p = d.project
  const busy = d.busy
  return jsxs('div', { className: 'flex flex-col gap-4', children: [
    jsxs('div', { className: 'flex items-center gap-3 flex-wrap', children: [
      jsx(Button, { variant: 'outline', size: 'xs', onClick: onBack, children: '← All films' }),
      jsx('div', { style: { fontSize: 16, fontWeight: 650, color: T.text }, children: p.name }),
      chip(p.status, p.film ? T.green : T.cyan),
      busy ? chip(`working: ${busy}`, T.amber) : null,
      jsxs('div', { style: { marginLeft: 'auto' }, className: 'flex items-center gap-2', children: [
        jsx('span', { style: label, children: 'Brand kit' }),
        jsx('select', {
          style: { background: T.card2, border: `1px solid ${T.line}`, borderRadius: 8, color: T.text, fontSize: 12, padding: '5px 8px' },
          value: p.brand,
          disabled: Boolean(busy),
          title: 'Applies this kit to the film: image style, palette, voices, music. Re-record voices after switching.',
          onChange: e => void act(`/project/${id}/brand`, `Brand kit set to ${e.target.value}. Images keep their look until regenerated; re-record voices to pick up the new kit.`, { brand: e.target.value }),
          children: brands.map(b => jsx('option', { value: b.id, children: b.name }, b.id)),
        }),
      ] }),
    ] }),
    jsx(Stepper, { p }),
    jsxs('div', { className: 'flex items-center gap-2 flex-wrap', children: [
      jsx(Button, { size: 'xs', disabled: Boolean(busy), style: { background: T.violet, color: '#fff' },
        onClick: () => sendToAgent(`Run the TVL Studio image loop for project '${id}': call studio_status, then follow next_action — generate each portrait/image with image_generate using the given prompt and reference_image_urls, attach with studio_attach_portrait / studio_attach_image, and repeat until next_action is voiceover. Then stop and report.`),
        children: 'Generate images with agent' }),
      jsx(Button, { size: 'xs', variant: 'outline', disabled: Boolean(busy) || p.imaged < p.shots,
        onClick: () => void act(`/project/${id}/voiceover`, 'Voiceover recording started — the board updates live.'),
        children: 'Record voices' }),
      jsx(Button, { size: 'xs', variant: 'outline', disabled: Boolean(busy) || p.voiced < p.shots,
        onClick: () => void act(`/project/${id}/assemble`, 'Assembly started — render takes 1–5 minutes.'),
        children: 'Assemble film' }),
      d.film ? jsx(Button, { size: 'xs', style: { background: T.green, color: '#04121a' },
        onClick: () => sendToAgent(`Show me the finished TVL Studio film for project '${id}' — deliver it with MEDIA:${d.film}`),
        children: 'Watch film in chat' }) : null,
    ] }),
    note ? jsx('div', { style: { fontSize: 12, color: T.green }, children: note }) : null,
    err ? jsx('div', { style: { fontSize: 12, color: T.red }, children: err }) : null,
    jsxs('div', { className: 'flex items-center gap-2 flex-wrap', children: [
      jsx('span', { style: label, children: 'Cast' }),
      Object.entries(d.cast).map(([name, c]) =>
        jsxs('div', { className: 'flex items-center gap-2', style: { background: T.card, border: `1px solid ${T.line}`, borderRadius: 20, padding: '3px 10px 3px 4px' }, children: [
          c.thumb ? jsx('img', { src: c.thumb, alt: '', style: { width: 22, height: 22, borderRadius: 11, objectFit: 'cover' } })
            : jsx('span', { style: { width: 22, height: 22, borderRadius: 11, background: T.card2, display: 'inline-block' } }),
          jsx('span', { style: { ...mono, fontSize: 10, color: T.text }, children: name }),
          jsx('span', { style: { ...mono, fontSize: 9, color: T.muted }, children: c.voice }),
        ] }, name)),
    ] }),
    jsxs('div', { style: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 },
      children: d.shots.map(s => jsx(ShotCard, { s, cast: d.cast }, s.id)) }),
    d.film ? jsxs('div', { style: { background: T.card, border: `1px solid ${T.green}44`, borderRadius: 12, padding: 14 }, className: 'flex flex-col gap-1', children: [
      jsx('div', { style: { fontSize: 13, color: T.green, fontWeight: 600 }, children: `Film ready — ${d.film_duration || '?'}s` }),
      jsx('div', { style: { ...mono, fontSize: 10.5, color: T.muted, wordBreak: 'break-all' }, children: d.film }),
    ] }) : null,
  ] })
}

function Page({ ctx }) {
  const gateway = useValue(host.state.gateway)
  const [projects, setProjects] = useState([])
  const [brands, setBrands] = useState([])
  const [open, setOpen] = useState(null)
  const [importing, setImporting] = useState(false)
  const [err, setErr] = useState('')
  const load = useCallback(async () => {
    try {
      const [ps, bs] = await Promise.all([ctx.rest('/projects'), ctx.rest('/brands')])
      setProjects(ps.projects); setBrands(bs.brands)
    } catch (e) { setErr(String((e && e.message) || e)) }
  }, [ctx])
  useEffect(() => { void load() }, [load])
  useEffect(() => ctx.setInterval(() => { if (!open) void load() }, 6000), [ctx, open, load])

  return jsxs('div', {
    className: 'flex h-full min-h-0 flex-1 flex-col gap-4 overflow-y-auto p-5',
    style: { background: T.bg, color: T.text },
    children: [
      jsxs('div', { className: 'flex items-center gap-3', children: [
        jsxs('div', { children: [
          jsx('div', { style: { ...mono, fontSize: 15, fontWeight: 700, letterSpacing: '0.18em', color: T.text }, children: 'TVL STUDIO' }),
          jsx('div', { style: { ...label, marginTop: 2 }, children: 'script → storyboard → images → voices → film' }),
        ] }),
        jsx(Badge, { variant: 'outline', children: `build ${BUILD}` }),
        jsx('span', { style: { ...mono, fontSize: 10, color: T.muted, marginLeft: 'auto' }, children: `gateway ${gateway}` }),
        jsx(Button, { size: 'xs', style: { background: T.violet, color: '#fff' }, onClick: () => { haptic('tap'); setImporting(true); setOpen(null) }, children: '+ New film' }),
      ] }),
      err ? jsx('div', { style: { fontSize: 12, color: T.red }, children: err }) : null,
      importing ? jsx(ImportPanel, { ctx, brands, onClose: () => setImporting(false), onDone: (id) => { setImporting(false); setOpen(id); void load() } }) : null,
      open ? jsx(ProjectView, { ctx, id: open, brands, onBack: () => { setOpen(null); void load() } })
        : jsxs('div', { className: 'flex flex-col gap-3', children: [
            projects.length === 0 && !importing ? jsxs('div', { style: { background: T.card, border: `1px solid ${T.line}`, borderRadius: 14, padding: 22 }, className: 'flex flex-col gap-2', children: [
              jsx('div', { style: { fontSize: 14, fontWeight: 600 }, children: 'No films yet.' }),
              jsx('div', { style: { fontSize: 12.5, color: T.muted, lineHeight: 1.6 }, children: 'Import a script and the studio builds the storyboard: one image per shot, one voice per character, captions timed to the dialogue, and a rendered MP4 at the end. Press “+ New film” and use the sample script to see the whole pipeline.' }),
            ] }) : null,
            jsxs('div', { style: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 14 }, children: projects.map(p =>
              jsxs('button', {
                type: 'button',
                onClick: () => setOpen(p.id),
                style: { background: T.card, border: `1px solid ${T.line}`, borderRadius: 14, padding: 16, textAlign: 'left', cursor: 'pointer', color: T.text },
                className: 'flex flex-col gap-2',
                children: [
                  jsxs('div', { className: 'flex items-center gap-2', children: [
                    jsx('span', { style: { fontSize: 13.5, fontWeight: 600 }, children: p.name }),
                    jsx('span', { style: { marginLeft: 'auto' }, children: chip(p.status, p.film ? T.green : T.cyan) }),
                  ] }),
                  jsx('div', { style: { ...mono, fontSize: 10.5, color: T.muted }, children: `${p.shots} shots · ${p.imaged} imaged · ${p.voiced} voiced · kit ${p.brand}` }),
                  jsx('div', { style: { fontSize: 11, color: T.muted }, children: (p.cast || []).join(', ') || 'narrator only' }),
                ],
              }, p.id)) }),
          ] }),
    ],
  })
}

export default {
  id: 'tvl-studio',
  name: NAME,
  register(ctx) {
    ctx.register({ id: 'page', area: ROUTES_AREA, data: { path: '/tvl-studio' }, render: () => jsx(Page, { ctx }) })
    ctx.register({ id: 'nav', area: SIDEBAR_NAV_AREA, data: { path: '/tvl-studio', label: NAME, codicon: 'device-camera-video' } })
  },
}
