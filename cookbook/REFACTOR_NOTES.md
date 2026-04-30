# Cookbook refactor — morning notes

Branch: `cookbook-refactor` (5 commits, not pushed). Delete this file when read.

## What changed

- **Cypress regression net** added in `cookbook/cypress/`. Smoke spec covers
  recipes-list render, recipe detail, edit-form mutate+persist roundtrip,
  chefs view. Login bypasses hCaptcha by sending `Token <auth_token>` as the
  password (the backend's login endpoint already accepts that).
- **Backend pytest suite** added in `backend/api/cookbook/tests/`. 8 tests:
  GET shape, FK by `_id`, M2M `tag_ids`, nested ingredients/steps/tips
  roundtrip, plus a "PATCH returns read shape" assertion that pins down
  the new contract.
- **Backend serializers** rewritten in `backend/api/cookbook/serializers.py`.
  Dropped the `api.frontend.serializers.ModelSerializer` base (with its
  `get_fields()` field-swap magic) for plain DRF `ModelSerializer` plus a
  small `NestedParentMixin` for owned reverse-relation create/update.
  Non-owned FK / M2M fields now expose paired `(read nested, write _id)`.
- **Frontend API layer** in `cookbook/src/api/`. One module per entity
  (`recipes.js`, `chefs.js`, `ingredients.js`, `units.js`,
  `recipeDifficulties.js`, `recipeRequiredTimes.js`, `recipeTags.js`,
  `menus.js`, `auth.js`, `translations.js`). All HTTP funnels through
  `client.js` (configured axios instance). The recipes module is the only
  one that translates read-shape -> write-shape (`chef_id`, `tag_ids`, ...).
- **Pinia stores** in `cookbook/src/stores/`. `defineByIdStore` factory
  produces consistent `byId`/`list`/`fetchAll`/`fetchOne`/`save` stores;
  reference data (chefs, units, tags, etc.) is persisted via
  `pinia-plugin-persistedstate`. Recipes are NOT persisted (large blobs,
  photo dicts).
- **Views/components migrated** off `composables/connector.js` (now deleted).
  `RecipesView`, `RecipeView`, `EditRecipeView`, `ChefsView`,
  `ProfileSettings`, `IngredientInput`, `LoginForm` — all use the stores +
  api modules. Old `console.log`s in `EditRecipeView` are gone.

## What I skipped (per scope)

- `backend/cookbook/signals.py` Groq classifier — left as-is. Tests
  monkeypatch `settings.GROQ_API_KEY = ""` to stop it firing on
  Ingredient creation.
- Migration squashing.
- Czech-strings → translation table migration.
- Form-level backend error display rework.
- TypeScript migration.

## Test fixture caveat

The `recipe` pytest fixture uses an in-memory PNG written via
`SimpleUploadedFile` so the `ThumbnailImageField` post_save signal can
`Image.open()` it without a `FileNotFoundError`. The Cypress edit test
also has to pick a recipe whose photo file actually exists on disk
(`unnamed_2.jpg.jpeg`, recipe id 21 in the dev DB) — a few of the seeded
recipes reference photos that aren't on the dev volume and would 500 on
PATCH. Worth seeding a media-rebuild step at some point, but out of
scope here.

## Surprises and gotchas

- **PATCH-with-photo-dict 200s**. When the frontend round-trips the read
  payload (which includes `photo: {small, medium, large, original}`),
  DRF's ImageField silently ignores the dict on PATCH and the existing
  file is kept. The new `api/recipes.toWritePayload` helper does NOT
  strip this for the same reason — it works, and stripping it would
  require knowing whether to send a fresh upload vs leave-as-is. The
  `image` form input wraps new uploads in `{base64data}`, which
  `client.js#stripFileWrappers` unwraps before sending.
- **Form `@keydown.enter="save"` + `cy.type` newlines**. Initially I tried
  `\n` to inject a marker; that fires the form submit. Switched to a
  literal space.
- **ESLint flat config + pre-commit**. The `files: ["cypress/**/*.js"]`
  glob has to be `**/cypress/**/*.js` because pre-commit invokes eslint
  from the repo root with paths like `cookbook/cypress/...`.
- **Cypress in cookbook**. Installed on the host (under `cookbook/`),
  not in the docker container — the alpine `bis-cookbook` image has no
  X libs. Run with `cd cookbook && npx cypress run`.

## How to run

```sh
# Backend
docker exec bis-backend pytest api/cookbook/tests/

# Frontend (cookbook needs to be reachable at http://localhost/cookbook/)
cd cookbook && npx cypress run --spec cypress/e2e/smoke.cy.js
```

## Suggested follow-ups (intentionally out of scope)

- Backfill the Phase 2 fixture chef into `backend/bis/management/commands/testing_db.py`
  so the Cypress test doesn't require the existing dev seed.
- Rebuild the media volume so all seeded recipes have intact photo files.
- Migrate Czech strings to the existing translations YAML.
- Squash the 9 cookbook migrations.
