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

## Exports and imports

- write and export only one react component per file, small helper components
  included; a file that already holds several is no reason to add another
- don't use default exports
- use absolute paths for imports when possible

## Components

### Share markup, don't copy it

When two components look the same but keep their data differently (in a form,
saved to the server right away), pull the look out into a component that only
takes props and renders, and build both on top of it. A copy of the markup
means every later change to the look has to be made twice.
[`FileGrid`](../src/components/ImageUpload/FileGrid.tsx) and
[`UploadedFile`](../src/components/ImageUpload/UploadedFile.tsx) are shared by
`ImagesUpload` (form) and `DirectFilesUpload` (direct upload).

### Keys

- When displaying array of items, use key (see [docs](https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key)).
  Use values, which 1) are unique among items, 2) do not change in time, ideally the following:
  1. Intrinsic id (or slug) of the item (mostly when item is downloaded from the backend).
  2. Array index. This is **only** OK when no components (only elements) are used to display items
     (simple components without state or effects would be OK, but you never know when this changes).
  3. Generated index (use `useRef` to store the counter). Index must be stored in state with the items.
     **Do not use this for items from props!** Or better, use (or extend) [useArrayState](../src/hooks/useArrayState.ts).
- Keys only have to be unique among the items of one array. Two `.map()`s next
  to each other don't need prefixes to keep their keys apart.

### Name what failed

When several things can fail at once (files of one upload), the error message
says which one: `Soubor ${file.name} se nepodařilo uložit`.

## Styles

We style components using [CSS modules](https://github.com/css-modules/css-modules) with [scss](https://sass-lang.com/)

- each component file should have its own separate CSS module.
- CSS module should be placed in the same folder as the component it belongs to, and be named `ComponentName.module.scss`
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
