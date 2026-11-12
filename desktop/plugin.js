// example-plugin — desktop half. Loads UNCOMPILED (no JSX): jsx()/jsxs() only.
// Imports are limited to @hermes/plugin-sdk, react, react/jsx-runtime. Everything
// else fails to resolve on purpose, and the catalog's `desktop surface` check
// refuses prototype patching, eval, and reaching into the app's own markup.
import { host, haptic, useValue, Badge, Button, ROUTES_AREA, SIDEBAR_NAV_AREA } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'

const BUILD = '0.1.0 · ui1'    // bump on every UI change — how you know the app reloaded
const NAME = 'Example Plugin'

function Page({ ctx }) {
  const gateway = useValue(host.state.gateway)
  const model = useValue(host.state.model) || 'this session\u2019s model'

  return jsxs('div', {
    // A page must be its OWN scroll container: `h-full` alone resolves to `auto`
    // under a route host with no height, and the content is clipped with nothing
    // to scroll. `min-h-0 flex-1` covers a flex host; `h-full` covers a fixed one.
    className: 'flex h-full min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-4',
    children: [
      jsxs('div', { className: 'flex items-center gap-2', children: [
        jsx('div', { className: 'text-[0.9375rem] font-semibold', children: NAME }),
        jsx(Badge, { variant: 'outline', children: `build ${BUILD}` }),
        jsx('span', { className: 'text-[0.75rem] text-(--ui-text-tertiary)', children: `gateway ${gateway} · ${model}` }),
      ]}),
      jsxs('div', {
        className: 'rounded-xl border border-(--ui-stroke-tertiary) bg-(--ui-bg-elevated) p-4 flex flex-col gap-2',
        children: [
          jsx('div', { className: 'text-[0.875rem] font-medium', children: 'Replace this card with the product.' }),
          jsx('div', { className: 'text-[0.75rem] text-(--ui-text-tertiary)', children: 'This page is inside the app shell and scrolls on its own. Every colour is a theme variable, so it reskins with the app.' }),
          jsx(Button, {
            variant: 'outline', size: 'xs',
            onClick: () => { haptic('tap'); host.notify({ kind: 'info', message: 'Replace this with a real action.' }) },
            children: 'Example action',
          }),
        ],
      }),
    ],
  })
}

export default {
  id: 'example-plugin',      // must equal the folder name
  name: NAME,
  register(ctx) {
    ctx.register({ id: 'page', area: ROUTES_AREA, data: { path: '/example-plugin' }, render: () => jsx(Page, { ctx }) })
    ctx.register({ id: 'nav', area: SIDEBAR_NAV_AREA, data: { path: '/example-plugin', label: NAME, codicon: 'symbol-event' } })
  },
}
