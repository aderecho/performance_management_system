# Frontend Engineering Skill

## Purpose
Handle frontend work for the `perf-mgt-fe` Quasar/Vue application, including UI development, routing, state management, API integration, forms, validation, charts, and frontend verification.

---

## Current Frontend Stack

- Framework: Vue 3.5.20
- UI Framework: Quasar 2.18.5
- Build Tool: Quasar CLI with Vite via `@quasar/app-vite` 2.6.0
- Quasar Extras: `@quasar/extras` 1.17.0
- State Management: Pinia 3.0.3
- Routing: Vue Router 4.5.1
- API Client: Axios 1.17.0
- Authentication Token Helper: jwt-decode 4.0.0
- Forms: vee-validate 4.15.1
- Schema Validation: `@vee-validate/zod` 4.15.1
- Internationalization: vue-i18n 11.1.12 with `@intlify/unplugin-vue-i18n` 4.0.0
- Charts: ECharts 6.0.0
- Linting: ESLint 9.36.0, `eslint-plugin-vue` 10.5.0, `@eslint/js` 9.36.0
- Formatting: Prettier 3.6.2, `@vue/eslint-config-prettier` 10.2.0
- Build Checking: vite-plugin-checker 0.10.3
- CSS Tooling: PostCSS 8.5.15, Autoprefixer 10.4.21
- Package Manager: npm

This project does not use Tailwind as the frontend styling standard. Prefer Quasar components, Quasar utility classes, and scoped Vue styles.

---

## Repository Layout

Frontend root:

```text
perf-mgt-fe/
+-- package.json
+-- quasar.config.js
+-- eslint.config.js
+-- postcss.config.js
+-- src/
```

Main `src/` layout:

```text
src/
+-- App.vue
+-- assets/
+-- boot/
|   +-- axios.js
|   +-- i18n.js
|   +-- theme.js
+-- components/
|   +-- admin/
|   +-- layout/
|   +-- pme/
+-- css/
|   +-- app.scss
|   +-- quasar.variables.scss
+-- helpers/
+-- i18n/
+-- layouts/
+-- pages/
+-- router/
|   +-- guards/
+-- stores/
+-- utils/
+-- validators/
```

---

## Quasar UI Rules

Prefer Quasar components and utility classes for UI structure and behavior.

Use Quasar components such as:

- `q-layout`, `q-page`, `q-drawer`, `q-header`
- `q-card`, `q-card-section`, `q-card-actions`
- `q-table`, `q-markup-table`
- `q-dialog`
- `q-form`, `q-input`, `q-select`
- `q-btn`, `q-icon`, `q-tooltip`
- `q-skeleton`
- `q-linear-progress`
- `q-chip`, `q-avatar`, `q-badge`

Use Quasar Notify through the existing notification utility where possible.

Prefer Quasar utility classes for common layout and spacing:

- `row`, `column`, `items-center`, `justify-between`, `justify-center`
- `q-pa-*`, `q-ma-*`, `q-mt-*`, `q-mb-*`, `q-gutter-*`
- `text-*`, `text-weight-*`, `bg-*`, `rounded-borders`, `shadow-*`

Use scoped CSS only for:

- Custom grids
- Custom chart or gauge shapes
- Responsive behavior that Quasar classes cannot express cleanly
- Component-specific layout constraints

Do not add Tailwind dependencies or Tailwind-style class systems unless the project explicitly adopts Tailwind later.

---

## Styling And Theme Rules

Theme variables live in:

```text
src/css/quasar.variables.scss
```

Global app styles live in:

```text
src/css/app.scss
```

Rules:

- Use Quasar theme colors before hard-coded colors when possible.
- Keep shared/global styling in `app.scss`.
- Keep component-only styling scoped inside the `.vue` file.
- Avoid large custom CSS blocks when Quasar components or utilities are enough.
- Keep cards at modest border radii unless the existing design requires otherwise.
- Ensure text fits on mobile and desktop.

---

## Component Rules

Use Vue 3 Composition API and `<script setup>`.

Prefer:

- Small, focused components.
- Domain components under `components/pme/`.
- Admin components under `components/admin/`.
- Layout shell components under `components/layout/`.
- Shared generic components directly under `components/`.

Avoid:

- Duplicating API calls across components when a Pinia store already owns the workflow.
- Putting large business workflows directly in templates.
- Creating one-off global components for a single page need.
- Mixing unrelated admin, PME, and layout behavior in one component.

When building tables, dialogs, filters, and forms, follow existing Quasar patterns in the repo before introducing new UI structure.

---

## State Management Rules

Use Pinia stores under:

```text
src/stores/
```

Current stores include:

- `auth.js`
- `config.js`
- `core.js`
- `pme.js`
- `user.js`

Rules:

- Keep API-backed workflows in stores when they are shared by pages/components.
- Keep transient local UI state in components when it is not shared.
- Use store actions for async calls.
- Keep getters simple and derived from store state.
- Use `acceptHMRUpdate` for stores, matching existing files.

---

## API Integration Rules

Use the shared Axios instance from:

```text
src/boot/axios.js
```

Rules:

- Import API calls with `import { api } from 'src/boot/axios'`.
- Do not create new Axios instances casually.
- Keep `withCredentials: true` because backend authentication uses HttpOnly JWT cookies.
- Let the existing Axios interceptor handle `401` token refresh.
- Do not store access or refresh tokens in local storage.
- Use `src/utils/notify.js` for user-facing success/error feedback.

Default API base behavior:

```js
process.env.API_BASE_URL || 'http://localhost:8000/api/v1'
```

---

## Routing And Auth Rules

Routes live in:

```text
src/router/routes.js
```

Auth guard lives in:

```text
src/router/guards/authGuard.js
```

Rules:

- Use lazy-loaded page components.
- Use `MainLayout.vue` for authenticated app pages.
- Use `meta.requiresAuth` for protected routes.
- Keep route auth decisions in `authGuard.js`.
- Keep route helpers in `src/router/routeHelpers.js`.
- Redirect unauthenticated users to `/login`.
- Redirect authenticated users away from `/login`.

---

## Forms And Validation

Use vee-validate with zod schemas for non-trivial forms.

Validation schemas live in:

```text
src/validators/
```

Current schema files include:

- `auth.schema.js`
- `initiative.schema.js`
- `user.schema.js`

Rules:

- Keep reusable validation outside page components.
- Use Quasar inputs with validation state from vee-validate.
- Keep API validation errors visible and understandable.
- Do not duplicate complex validation rules across components.

---

## Charts And Data Visualization

Use ECharts for charting.

Rules:

- Initialize charts after the DOM element is mounted.
- Dispose chart instances in `onBeforeUnmount`.
- Handle resize behavior when charts need responsive sizing.
- Prefer derived/computed chart data from stores or props.
- Avoid hand-rolling complex charts when ECharts can represent the view.

---

## Internationalization

Vue I18n is configured through:

```text
src/boot/i18n.js
src/i18n/
```

Rules:

- Put translatable app strings in i18n files when the feature is user-facing and likely to be reused.
- Keep short internal labels inline only when the surrounding feature already does so.
- Do not bypass the existing i18n boot setup.

---

## Verification Commands

Use these commands from `perf-mgt-fe/`:

```bash
npm.cmd run lint
npm.cmd run build
```

On Windows PowerShell, use `npm.cmd` when `npm` is blocked by script execution policy.

Project scripts:

```bash
npm.cmd run dev
npm.cmd run lint
npm.cmd run build
npm.cmd run format
```

Run lint/build after meaningful frontend edits. Do not run `format` unless formatting changes are explicitly desired.

---

## AI Agent Instructions

Before coding:

1. Inspect existing page/component/store patterns.
2. Prefer Quasar components and utility classes over custom CSS.
3. Reuse Pinia stores and shared Axios setup.
4. Check route/auth behavior before adding pages.
5. Check existing validators before adding form rules.

Before finishing:

1. Run `npm.cmd run lint`.
2. Run `npm.cmd run build` for substantial changes.
3. Verify responsive behavior for changed pages/components.
4. Confirm no tokens or secrets are stored in frontend code.
5. Confirm API paths match backend `/api/v1` routes.

Never:

- Add Tailwind classes or config unless Tailwind is intentionally adopted.
- Store JWT tokens in local storage.
- Create duplicate Axios clients without a clear need.
- Bypass the route auth guard for protected pages.
- Put shared API workflows only inside leaf components.
- Leave chart instances undisposed.
