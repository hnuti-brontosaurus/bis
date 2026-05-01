# Tasks

Backlog of follow-ups that intentionally fall outside the immediate refactor
scope. Add to this list when you defer something; remove items as they ship.

## Cookbook

- Squash cookbook migrations once schema stabilizes. Currently 17 migrations
  with renames/re-adds — see `backend/cookbook/migrations/`.
- Wire `:backend-errors` into the remaining forms that share `GenericForm`:
  Profile (`components/auth/ProfileSettings.vue`),
  Login (`components/auth/LoginForm.vue`),
  Ingredient creation dialog (`contrib/components/IngredientInput.vue`).
  They all already render through `GenericForm`, so it's just a `backendErrors`
  ref + try/catch around the save call.
- Render deep-nested DRF errors better. The current `GenericForm` flattens
  `{field: ["msg", ...]}` into the field's feedback slot; nested shapes like
  `ingredients[2].amount: ["..."]` fall back to `JSON.stringify` which is
  visible but ugly.
- Backfill the Phase 2 fixture chef into
  `backend/bis/management/commands/testing_db.py` so the Cypress test does
  not require the existing dev seed.
- Rebuild the media volume so all seeded recipes have intact photo files
  (a few seeded recipes reference photos that aren't on the dev volume and
  would 500 on PATCH).
- Migrate Czech strings to the existing translations YAML for any new
  `.vue` files added after the Phase 3 audit.
- Add a Cypress spec for the form-error display path. Currently only the
  golden-path smoke is covered; would need a way to trigger a 400 (the
  recipe form is permissive).
