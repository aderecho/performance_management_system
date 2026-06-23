# Frontend Development

## Purpose

Build maintainable, accessible, responsive, secure, and production-ready frontend features while respecting the current project's technology stack, architecture, conventions, and design system.

This skill is reusable across frontend projects, including projects built with:

* React
* Vue
* Angular
* Svelte
* Solid
* Next.js
* Nuxt
* Remix
* Astro
* Vite
* Webpack
* JavaScript
* TypeScript
* CSS, Sass, or Less
* Tailwind CSS
* Bootstrap
* Material UI
* Quasar
* PrimeVue
* Chakra UI
* Other frontend technologies

Do not assume that any specific framework, library, or tool is installed.

---

# Core Principles

Follow these principles in every frontend task:

1. Inspect the project before making changes.
2. Follow existing project conventions.
3. Reuse existing components, utilities, services, and design tokens.
4. Prefer the smallest complete solution.
5. Keep responsibilities clearly separated.
6. Avoid unnecessary dependencies.
7. Preserve backward compatibility unless a breaking change is required.
8. Handle loading, empty, success, and error states.
9. Ensure responsive and accessible behavior.
10. Validate the implementation using the project's available commands.

---

# Project Discovery

Before implementing a task, inspect the project to determine its actual stack and conventions.

Check relevant files such as:

```text
package.json
package-lock.json
pnpm-lock.yaml
yarn.lock
bun.lock
tsconfig.json
jsconfig.json
vite.config.*
webpack.config.*
next.config.*
nuxt.config.*
angular.json
svelte.config.*
astro.config.*
tailwind.config.*
postcss.config.*
eslint.config.*
.eslintrc*
.prettierrc*
src/
app/
pages/
components/
routes/
router/
stores/
services/
tests/
```

Identify:

* frontend framework
* framework version
* JavaScript or TypeScript usage
* package manager
* build tool
* routing solution
* state-management solution
* styling approach
* UI component library
* form library
* validation library
* HTTP client
* testing tools
* linting and formatting tools
* folder structure
* naming conventions
* import aliases
* design system or theme
* existing reusable components
* available project commands

Do not introduce a tool merely because it is commonly used.

---

# Technology Selection Rules

Use the project's existing stack whenever possible.

Examples:

* If the project uses React, follow its React patterns.
* If the project uses Vue, follow its Vue patterns.
* If the project uses Angular, follow its Angular patterns.
* If the project uses TypeScript, preserve strict typing.
* If the project uses JavaScript, do not convert unrelated files to TypeScript.
* If the project uses Tailwind CSS, follow its utility conventions.
* If the project uses a component library, reuse its components.
* If the project uses an existing state manager, do not add another one.
* If the project already has an API client, use it.
* If the project already has a form-validation solution, reuse it.
* If the project has no testing framework, do not install one without a requirement.

When multiple valid patterns exist, prefer the pattern already used in nearby files.

---

# Working Process

For each frontend task:

1. Understand the requested behavior.
2. Inspect related routes, pages, components, services, stores, and tests.
3. Identify reusable project code.
4. Determine the appropriate responsibility boundary.
5. Plan the smallest set of changes.
6. Implement the feature using existing conventions.
7. Handle all relevant interface states.
8. Review responsive and accessible behavior.
9. Run available validation commands.
10. Summarize the changes and any remaining limitations.

Do not begin with a major refactor unless the task requires it.

---

# Responsibility Boundaries

## Pages and Routes

Pages or route-level components should coordinate screen-level behavior.

They may:

* read route parameters
* load page-level data
* connect stores, services, and components
* enforce route-level user experience rules
* arrange feature sections
* manage page-level loading and error states

Pages should not contain large reusable UI implementations or unrelated business logic.

## Components

Components should represent focused, reusable interface units.

A component should:

* have a clear responsibility
* expose an understandable public interface
* receive data through the framework's supported input mechanism
* communicate changes through explicit events, callbacks, or bindings
* avoid hidden dependencies
* avoid unnecessary global state
* remain reasonably easy to test

Extract a component when a section:

* is reused
* has independent behavior
* has complex rendering logic
* makes the parent difficult to understand
* represents a meaningful interface concept

Do not split trivial markup into excessive components.

## State Management

Use local component state for state that belongs to one component or one small component tree.

Use shared state when data:

* is needed by unrelated components
* must persist across routes
* represents authentication or session information
* acts as a shared cache
* controls cross-feature workflows
* must remain synchronized across the application

Do not put temporary UI details into global state without a clear reason.

## Services and API Modules

Keep external communication separate from rendering logic when the project architecture supports it.

Service modules may handle:

* endpoint definitions
* request parameters
* response types
* response normalization
* request cancellation
* authentication headers
* shared error transformation

Avoid scattering endpoint URLs and request configuration throughout components.

## Utilities

Use utilities for pure, reusable operations such as:

* formatting
* parsing
* validation helpers
* data transformation
* sorting
* filtering
* date handling

Do not place framework-specific stateful logic in generic utility files.

## Hooks and Composables

Use the framework's reusable logic mechanism when logic:

* is stateful
* uses framework lifecycle behavior
* is needed in multiple components
* integrates with browser APIs
* manages reusable interactions

Examples include hooks, composables, services, directives, or framework-specific equivalents.

---

# Component Design Standards

Follow the conventions of the active framework.

Regardless of framework:

* keep components focused
* use clear names
* avoid hidden side effects
* avoid deeply nested rendering conditions
* avoid duplicated derived state
* keep business rules out of purely presentational components
* avoid mutating external inputs unexpectedly
* make data flow understandable
* prefer explicit behavior over clever abstractions
* document unusual decisions

Use the project's established filename convention, such as:

```text
PascalCase
camelCase
kebab-case
```

Do not rename existing files solely to enforce a personal preference.

---

# Type Safety

When the project uses TypeScript:

* define clear types for component inputs and outputs
* type API requests and responses
* type shared state
* use unions for known status values
* narrow unknown errors safely
* avoid unnecessary type assertions
* avoid `any`
* use `unknown` when the value genuinely requires validation
* preserve the project's strictness settings

Example:

```ts
type RequestStatus = 'idle' | 'loading' | 'success' | 'error'

interface User {
  id: string
  name: string
  email: string
}
```

Do not create duplicate types when an existing shared type is available.

When the project uses JavaScript, preserve clarity through naming, validation, and documentation where necessary.

---

# Forms and Validation

Follow the project's existing form and validation solution.

Every form should account for:

* initial values
* client-side validation
* server-side validation
* field-level errors
* form-level errors
* loading state
* duplicate submission prevention
* successful submission
* recoverable failure
* destructive-action confirmation when necessary

Validation rules should:

* match backend requirements
* produce understandable messages
* avoid relying exclusively on browser validation
* not replace server-side validation
* preserve user input after recoverable failures

Do not add a form library for a simple form unless the project already uses it or complexity justifies it.

---

# Data Fetching

When loading asynchronous data:

* use the project's existing API client
* expose loading state
* expose meaningful errors
* handle empty results
* prevent stale data from replacing newer data
* avoid duplicate requests where practical
* clean up subscriptions or pending work when appropriate
* paginate large datasets
* debounce user-driven searches when appropriate
* avoid fetching data that is not needed

Never display raw internal server errors directly to end users.

Do not silently ignore failures.

---

# Interface States

Every asynchronous screen should consider:

## Loading State

Show that work is in progress using an appropriate indicator, skeleton, placeholder, or disabled state.

## Empty State

Explain that no data is available and provide a useful next action when relevant.

## Error State

Provide a clear message and a retry or recovery action when possible.

## Success State

Show the resulting data or confirm that the requested operation succeeded.

## Unauthorized State

Hide or disable unauthorized actions for user experience, while relying on backend authorization for actual security.

Do not leave users with a blank screen.

---

# Routing and Navigation

Follow the project's routing system.

Routing rules:

* use named routes or route constants when the project supports them
* preserve browser history expectations
* use lazy loading for route-level code when appropriate
* validate required route parameters
* handle unavailable resources
* provide a not-found experience
* preserve redirect destinations during authentication when appropriate
* avoid hardcoded URLs when route helpers exist
* avoid deprecated routing APIs

Frontend route guards improve user experience but do not replace backend authorization.

---

# Styling

Follow the styling approach already used by the project.

Possible approaches include:

* plain CSS
* Tailwind
* CSS modules
* scoped CSS
* Sass or Less
* utility classes
* CSS-in-JS
* component-library styling APIs
* design-system tokens

Styling rules:

* reuse existing design tokens
* maintain consistent spacing
* maintain consistent typography
* maintain consistent colors
* maintain consistent border radii
* maintain consistent shadows
* avoid unnecessary inline styles
* avoid repeated magic values
* avoid `!important` unless unavoidable
* avoid adding global styles for component-specific behavior
* do not mix styling systems without a reason

When introducing reusable values, prefer the project's token or variable system.

---

# Responsive Design

Ensure the feature works across the breakpoints supported by the project.

Check:

* content width
* navigation behavior
* table overflow
* form layout
* modal size
* touch targets
* text wrapping
* image scaling
* card arrangement
* action-button placement
* horizontal scrolling
* mobile keyboard behavior

Prefer layouts that adapt naturally rather than creating many device-specific rules.

Do not rely on hover-only interactions.

---

# Accessibility

Frontend work should follow accessibility best practices.

Ensure:

* semantic HTML is used where possible
* interactive elements are keyboard accessible
* visible focus states are preserved
* buttons have understandable names
* inputs have labels
* validation messages are associated with fields
* headings follow a logical order
* dialogs manage focus appropriately
* icon-only actions have accessible labels
* color is not the only indicator of meaning
* contrast is readable
* dynamic updates are communicated when necessary
* images have appropriate alternative text
* decorative images are ignored by assistive technology

Prefer native semantic elements before recreating their behavior.

---

# Security

Frontend code must not be treated as a secure boundary.

Follow these rules:

* never expose secrets in client-side source code
* never trust client-side authorization alone
* avoid rendering unsanitized HTML
* validate external URLs before navigation where relevant
* do not log tokens or sensitive personal information
* do not expose sensitive values in query parameters
* follow the project's authentication-storage strategy
* protect against unsafe redirects
* validate uploaded file type and size on the client while relying on server validation
* keep dependencies updated through the project's normal process
* do not weaken security checks for convenience

Do not use unsafe HTML-rendering features with untrusted data.

---

# Performance

Optimize based on evidence and meaningful user impact.

Consider:

* route-level code splitting
* lazy loading
* image optimization
* request caching
* pagination
* list virtualization
* memoization
* reducing unnecessary renders
* reducing unnecessary reactive dependencies
* avoiding expensive template calculations
* debouncing frequent user input
* avoiding oversized dependencies
* reducing duplicate network requests
* cleaning up listeners and subscriptions

Do not introduce complex optimization without a demonstrated need.

---

# Error Handling

Handle errors at the appropriate level.

Use:

* field errors for invalid inputs
* component errors for local failures
* page errors for route-level failures
* global handlers for authentication or application-wide failures

Error messages should:

* be understandable
* avoid exposing implementation details
* explain what the user can do next
* preserve recoverable user input
* distinguish validation errors from system failures

Do not catch errors only to ignore them.

---

# Testing

Use the testing tools already configured in the project.

Prioritize tests for:

* critical user workflows
* form validation
* permission-dependent behavior
* loading states
* empty states
* errors and retries
* component interactions
* state-management actions
* routing behavior
* data transformation
* regression-prone logic

Test observable behavior rather than internal implementation details.

Avoid adding low-value tests merely to increase coverage.

Do not claim tests passed unless they were executed successfully.

---

# Dependency Management

Before installing a dependency:

1. Confirm the project does not already provide the needed functionality.
2. Check whether a small local implementation is simpler.
3. Confirm compatibility with the current stack.
4. Consider maintenance and bundle-size impact.
5. Use the project's existing package manager.
6. Avoid installing overlapping libraries.

Do not replace an existing library without a clear requirement.

Do not update unrelated packages during a focused feature task.

---

# Package Manager Detection

Detect the package manager from the lockfile:

```text
package-lock.json → npm
pnpm-lock.yaml    → pnpm
yarn.lock         → Yarn
bun.lock          → Bun
bun.lockb         → Bun
```

Use the detected package manager for all commands.

Do not generate a different lockfile.

---

# Validation Commands

Read `package.json` and use the scripts actually available in the project.

Common examples include:

```bash
npm run lint
npm run format
npm run type-check
npm run test
npm run test:unit
npm run test:e2e
npm run build
```

Use the equivalent command for the project's package manager.

Run the most relevant available checks after changes.

Do not invent scripts that are not defined.

Do not claim a command succeeded unless it was executed and completed successfully.

---

# Refactoring Rules

When refactoring:

* preserve existing behavior unless changes are requested
* keep the scope focused
* avoid unrelated formatting changes
* avoid renaming public interfaces without need
* remove duplication when it improves clarity
* simplify overly complex logic
* preserve tests or update them intentionally
* verify all affected call sites
* avoid creating abstractions used only once unless they improve understanding significantly

Do not combine a large architectural rewrite with a small feature request.

---

# Code Review Guidelines

When reviewing frontend code, check:

## Correctness

* Does it satisfy the requested behavior?
* Are edge cases handled?
* Are asynchronous operations safe?
* Are data transformations correct?

## Architecture

* Are responsibilities separated clearly?
* Is existing project structure followed?
* Is shared logic placed appropriately?
* Is the abstraction level justified?

## Maintainability

* Are names understandable?
* Is logic duplicated?
* Are components too large?
* Are comments explaining decisions rather than obvious syntax?

## User Experience

* Are loading, empty, error, and success states present?
* Is feedback immediate and understandable?
* Are destructive actions protected?

## Accessibility

* Is the interface keyboard accessible?
* Are labels and semantic elements used?
* Are focus and contrast handled?

## Security

* Is untrusted content handled safely?
* Are secrets or sensitive details exposed?
* Is authorization incorrectly trusted to the frontend?

## Performance

* Are unnecessary requests or renders present?
* Is a heavy dependency being introduced?
* Are large datasets handled appropriately?

## Testing

* Are critical behaviors covered?
* Do tests verify user-visible outcomes?
* Are regressions likely?

Clearly distinguish required fixes from optional improvements.

---

# Prohibited Practices

Avoid:

* assuming a framework before inspecting the project
* rewriting the project into a preferred stack
* introducing unnecessary dependencies
* mixing unrelated architecture patterns
* scattering API calls throughout UI components
* duplicating components already available
* storing all state globally
* using raw server errors as user messages
* hiding errors without feedback
* relying only on frontend authorization
* exposing secrets in frontend code
* using untrusted content with unsafe HTML rendering
* adding unrelated formatting changes
* modifying generated files manually
* claiming tests or builds passed without running them
* changing package managers
* generating a second lockfile
* performing large unrelated refactors

---

# Completion Checklist

Before completing a frontend task, verify:

* The actual project stack was inspected.
* Existing patterns were followed.
* No unnecessary dependency was added.
* Components have clear responsibilities.
* Data flow is understandable.
* Types are correct when TypeScript is used.
* Loading, empty, error, and success states are handled.
* Forms prevent duplicate submissions.
* Responsive behavior was considered.
* Accessibility basics are present.
* Sensitive data is not exposed.
* No unrelated files were changed.
* Relevant checks were executed when available.
* Remaining risks or limitations are documented.

---

# Response Format

After completing implementation work, report:

## Implemented

Briefly explain the completed behavior.

## Files Changed

List the files created, modified, or deleted.

## Technical Decisions

Explain important architecture, compatibility, or reuse decisions.

## Validation

List commands that were actually executed and their results.

## Remaining Notes

Mention known limitations, skipped checks, assumptions, or follow-up work.

Keep the final report focused on the requested task.
