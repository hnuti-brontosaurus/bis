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

# Cookbook refactor — afternoon notes (continuation)

3 more commits on top of the morning batch. Cypress (3/3) and pytest
(10/10) green. No push.

## Job 1 — Groq enrichment out of pre_save

- New module `backend/cookbook/services/ingredient_enrichment.py` holds
  the prompt and the `enrich_ingredient(instance) -> bool` call. Returns
  False when `GROQ_API_KEY=""` so dev environments still work; returns
  True after writing fields back onto the instance (caller re-saves).
- `backend/cookbook/signals.py` now does only the cheap normalization
  (whitespace collapse, capitalize-on-create). No network, no try/except,
  ~15 lines.
- `IngredientViewSet.perform_create` calls `enrich_ingredient` after the
  initial save; on success the instance is saved a second time. Errors
  from Groq are NOT swallowed — they bubble as a 500 to the API caller
  (the freshly-created Ingredient still exists).
- New `backend/api/cookbook/tests/test_ingredient_api.py` covers both
  paths (key empty, key set + mocked `groq.Groq`).
- Frontend `IngredientInput.vue` already uses
  `ingredientsStore.save({name})` + `handleAxiosError`; no changes
  needed there.

## Job 2 — Czech strings → translations

- Audited every `.vue` under `cookbook/src/` for hard-coded Czech.
  Findings: `RecipeView`, `RecipeIngrediences`, `EditRecipeView`,
  `ChefsView`, `HomeView`, `GenericForm`, `ProfileSettings`. (RecipeSteps
  exists but is not imported anywhere — left as-is.)
- Added keys under `cookbook.recipes.*`, `cookbook.edit_recipe.*`,
  `cookbook.home.*`, `cookbook.chefs.*`, `cookbook.ingredients.*`
  (the `create_*`/`upsert_error` keys the user's IngredientInput.vue
  already references), and `cookbook.profile.saved`.
- Replaced literal strings with `_.namespace.key` in templates,
  `_.value.namespace.key` in script blocks. Matches the
  `IngredientInput.vue` pattern.
- Fixed an existing `cookbook.section.tips: iip` typo (now `tip`).
- Renamed `_` callback params in `RecipeIngrediences.vue` (would shadow
  the translations alias).
- Final grep for Czech chars in `cookbook/src/**/*.vue` — clean.
- Backend `frontend/src/config/static/translations.ts` regenerated by
  the `generate-translations` pre-commit hook (used by the React
  frontend, not by the cookbook).

## Job 3 — Form error display

- `EditRecipeView` now catches DRF 400s from `recipesStore.save`,
  drops `error.response.data` into a `backendErrors` ref, and clears
  it at the start of each submit.
- `non_field_errors` render as an `n-alert` above the form.
- `GenericForm` accepts a new `:backend-errors` prop (default `{}`) and
  wires the matching message into each `n-form-item-gi` via the
  `feedback` + `validation-status` props. No deep nesting handled —
  noted as future work.
- Other forms (Profile, Login, Ingredient) use the same GenericForm
  shell, so the prop is available; they can opt in with a local
  `backendErrors` ref. Not done in this pass.

## Skipped / punted

- Deep nested DRF errors (e.g. `ingredients[2].amount`). The current
  pass only handles the top-level field map. Nested ones currently fall
  back to `JSON.stringify` in the feedback string — visible but ugly.
- Wiring backend errors into Profile/Login/Ingredient forms.
- Cypress coverage for the error-display path (would need a way to
  trigger a 400; the recipe form is permissive).

## Surprises

- The translations proxy uses `${group}.${key}` as the fallback string,
  so missing keys appear literally in the UI rather than throwing —
  easy to miss until you run the app. A grep for `\.value\.[a-z_]+\.[a-z_]+`
  vs the YAML is the only safety net.
- The `IngredientInput.vue` file the user pre-edited references several
  translation keys (`ingredients.create_title` etc.) that did NOT exist
  in the YAML before this pass. They were silently rendering as
  `ingredients.create_title`. Added them.
- `frontend/src/config/static/translations.ts` regenerates from the
  same yaml even though only the cookbook uses some of these keys —
  inflates the React bundle slightly, but the existing pipeline is
  what it is.

# Cookbook refactor — Round 2 (test isolation, \_id symmetry, data/ layer)

Five jobs, all folded into the original 10 commits via `--fixup` +
`rebase --autosquash master`. One new commit (`tasks.md`) sits on top.
Backend pytest 11/11, cypress 3/3 — both run alongside `make dev`.

## Job 1 — Test isolation

`docker-compose.test.yaml` + `nginx/test.conf` define an isolated stack
under compose project `bis-test`: separate containers (`bis-test-*`),
separate `postgresqldata_test` volume, single host port (8090) for
cypress to reach. `make test_backend`, `make test_frontend`,
`make test_cookbook` all bring up only what they need (via the
`backend` / `frontend` / `cookbook` profiles), seed a token user, and
tear down the volume on EXIT. `make test` runs all three. CI
(`.github/workflows/ci.yml`) already calls `make test` — no change
needed there. `.pre-commit-config.yaml` excludes
`docker-compose.test.yaml` from `check-yaml` (pyyaml chokes on the
`!override` tag compose v2.20+ uses).

## Job 2 — Symmetric `_id` on read AND write

Recipe and through-row serializers expose only `chef_id`,
`difficulty_id`, `required_time_id`, `tag_ids`, `ingredient_id`,
`unit_id` — no nested objects. PATCH(GET payload) is now a literal
round-trip; `test_recipe_get_then_patch_roundtrip` pins the contract.
Owned children (ingredients/steps/tips) still nest fully. Tests
updated; the old `cookbook_categories.serializers` import is gone.

## Job 3 — `cookbook/src/data/<entity>.js` consolidation

Each entity now lives in one file exporting `<entity>Api` (named
namespace, e.g. `recipesApi.list/get/save`) and `use<Entity>Store`
(Pinia). `cookbook/src/api/` and `cookbook/src/stores/` are gone.
`useRecipe(id)` composable in `data/recipes.js` returns a `computed`
that spreads the raw row plus resolved `chef`, `difficulty`,
`required_time`, `tags`, and per-row `ingredient`/`unit` — callsites
can use either `recipe.chef_id` (raw FK) or `recipe.chef` (resolved
object). Same pattern is available for any entity that grows FKs.

## Job 4 — Persistence tuning

All entity stores including recipes are persisted (via
`pinia-plugin-persistedstate` through the `defineByIdStore` factory).
Recipe images use a custom `serializer` that strips `base64data` /
`file` upload blobs before write — the URL fields
(`small/medium/large/original`) stay because they're cheap strings.
`PERSISTED_VERSION` constant in `data/factory.js` is the kill switch
for shape changes.

## Job 5 — `tasks.md`

Moved deferred items out of the refactor notes into a top-level
`tasks.md`: migration squash, remaining `:backend-errors` wiring on
Profile/Login/Ingredient forms, deep nested DRF error rendering,
fixture chef in `testing_db`, media volume rebuild.

## Surprises and gotchas (Round 2)

- **DRF pagination URLs leak the request Host.** The cookbook SPA
  used to pass `next` straight to axios, which under cypress (test
  stack on `:8090`, dev stack on `:80`) sent the followup request
  cross-origin to the dev stack — silently or with a 404. `fetchAll`
  in `data/client.js` now strips both the scheme+host AND the axios
  baseURL prefix from `next` so the SPA always talks to its own
  origin.
- **Make trap + cd.** `make test_cookbook` does `cd cookbook && npx
cypress run`; the EXIT trap then ran in `cookbook/` and docker
  compose tried to read `cookbook/.env` (which is malformed). Wrapped
  the cd in a subshell `(cd cookbook && npx cypress run)` so the trap
  fires from repo root.
- **Compose `!override` tag.** Needed to override `ports`/`volumes`
  in the test compose file so the test stack doesn't try to bind
  ports the dev stack already owns. pyyaml has no idea what
  `!override` is, so the `check-yaml` pre-commit hook excludes that
  one file.
- **`GenericForm.input.path` vs `input.key`.** The chef select uses
  `key: "chef"` (for the human-readable label via translations) but
  `path: "chef_id"` so the n-form-item validation path matches the
  raw FK on the data object. Shipping in GenericForm.vue as part of
  the canonical pattern the user wants.
