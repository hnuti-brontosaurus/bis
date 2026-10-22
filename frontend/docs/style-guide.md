# Style guide and best practices for this project

## Language

This project uses English, although primary text of the final application is Czech. We write comments, name files, folders, variables etc. in English. You'll find strings in czech language throughout the app, mostly where they need to be displayed. This may be refactored into translation files in the future.

## React

For best practices, refer to documentation of [React](https://reactjs.org/) and [Vite](https://vite.dev/)

These best practices are preferred when in conflict with practices of this project

Form-specific conventions live in [forms.md](forms.md).

## Naming conventions

### Files and folders

- follow the conventions that are already used throughout the project
- files that export react components should be named with `PascalCase.tsx`, so should be named organizing folders and stylesheets with the same name. e.g. `..../PascalCase/PascalCase.module.scss`
- typescript files that don't export react components (e.g. helpers, hooks, api, config) should be named with `camelCase.ts`
- other files (assets, docs, generic stylesheets) can be named with `kebab-case.svg`

### Variables

In Typescript, we name variables with `camelCase` or `PascalCase`.

In this project, some object properties are named by `snake_case`. We do that to simplify dealing with data returned from api. Otherwise this practice should be avoided in favor of `camelCase` and `PascalCase`.

### Constants

Name module-level constants with `UPPER_CASE`, so they are not mistaken for
variables.

```ts
const DEFAULT_TIMEOUTS = { success: 4_000, error: 12_000 } as const
```

## User-facing text

Write Czech strings directly where they are displayed. `config/static/translations.ts`
is generated from the backend yamls for the names of models, fields and
choices; don't add strings of a single component to it.

## Code structure

### Keep handlers out of the markup

A handler longer than a few lines doesn't belong inline in JSX. Give it a name
and define it above the `return`, or move the logic into a hook (see
[forms.md](forms.md#extract-async-operations-into-a-hook)).

### Promises

- Call `resolve` and `reject` directly. Don't wrap them in a function that
  decides between them by the type of its argument.
- A cancelled dialog or a declined confirmation is not an error. Resolve with
  `null` (or `false`) and let the caller return early, instead of rejecting
  and filtering the rejection out again.
- Wrap a callback-style API in a helper that returns a promise, once, instead
  of building the plumbing at every call site. [`openModal`](../src/utils/openModal.tsx)
  does this for `react-confirm-alert`:

```tsx
const user = await openModal<User>({
  title: 'Zadat datum narození',
  message: user.display_name,
  render: close => <BirthdayForm onSubmit={…} onCancel={() => close(null)} />,
})
if (!user) return
```

### Errors

- Don't swallow errors. Every `catch` either shows the error to the user or
  rethrows it; a `catch` that doesn't recognise an error rethrows it.
- To tell one kind of error from another, define an error class and check it
  with `instanceof`. Never compare `error.message`: the message is text for
  the user and may change.

```ts
class LockedOutError extends Error {}

if (error instanceof LockedOutError) …
```

## Exports and imports

- write and export only one react component per file
- don't use default exports
- use absolute paths for imports when possible

## Styles

We style components using [css modules](https://github.com/css-modules/css-modules) with [scss](https://sass-lang.com/)

- css module should be placed in the same folder as the component it belongs to, and be named `ComponentName.module.scss`
- other stylesheets should be placed in `src/styles`

## Commit messages

We care about commit messages.

There are some [good resources](https://www.freecodecamp.org/news/writing-good-commit-messages-a-practical-guide/) suggesting how to write a good commit message.

When a pull request contains many related small commits, we _squash_ and merge when merging to `main` branch. There are exceptions to this rule, e.g. when your commits in the PR are independent and large. When in doubt, squash!

We follow at least these rules for commit messages:

- Capital first letter of the message (on the first line)
- Imperative style commit message
- Don't end the first line with period
- Follow the first line with empty line
- Then write more freely what you did in more detail

Please follow at least these rules. Feel free to improve them, e.g. specify type of the commit, provide issue it fixes, ...

Run `git log` to see examples.

## Comments

Comment language is English.

Default to no comments. Code with well-named identifiers explains itself &mdash;
when it doesn't, rewrite the code to be more readable rather than describing it
in prose.

Write a comment only for a non-obvious **why**: a constraint, an invariant, a
workaround for a specific bug, or behavior that would surprise a reader.
Linking the source of a workaround (an issue, a stack overflow answer) is
useful; the link belongs in the comment that explains the constraint.

```tsx
// never `undefined` — that would flip the input to uncontrolled and
// React would leave the previously typed value in the DOM when the
// form clears the field
value={value ?? ''}
```

Don't write:

- section banners (`// ---- Helpers ----`)
- restatements of the next line
- references to tasks, PRs or tickets
- commented-out code &mdash; that's what git history is for
- framework template boilerplate

If deleting the comment wouldn't confuse a competent reader, don't write it.

The same rules are stated in [CLAUDE.md](../../CLAUDE.md) so that AI-assisted
changes follow them too. Plenty of existing comments predate this policy &mdash;
don't take the current state as an example worth following.
