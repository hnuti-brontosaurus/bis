import { client, fetchAll, upsert } from "./client.js"

const path = "/recipes"

/**
 * The frontend stores recipes in the read shape (`chef`, `difficulty`, ...
 * as nested objects). The backend writes accept `chef_id`, `difficulty_id`
 * etc. Translate at the boundary.
 */
const toWritePayload = recipe => {
  const out = { ...recipe }
  if (out.chef && typeof out.chef === "object") {
    out.chef_id = out.chef.id
    delete out.chef
  }
  if (out.difficulty && typeof out.difficulty === "object") {
    out.difficulty_id = out.difficulty.id
    delete out.difficulty
  }
  if (out.required_time && typeof out.required_time === "object") {
    out.required_time_id = out.required_time.id
    delete out.required_time
  }
  if (Array.isArray(out.tags)) {
    out.tag_ids = out.tags.map(t => (typeof t === "object" ? t.id : t))
    delete out.tags
  }
  if (Array.isArray(out.ingredients)) {
    out.ingredients = out.ingredients.map((row, order) => {
      const r = { ...row, order }
      if (r.ingredient && typeof r.ingredient === "object") {
        r.ingredient_id = r.ingredient.id
        delete r.ingredient
      }
      if (r.unit && typeof r.unit === "object") {
        r.unit_id = r.unit.id
        delete r.unit
      }
      return r
    })
  }
  if (Array.isArray(out.steps)) {
    out.steps = out.steps.map((row, order) => ({ ...row, order }))
  }
  if (Array.isArray(out.tips)) {
    out.tips = out.tips.map((row, order) => ({ ...row, order }))
  }
  // Comments are read-only on the parent serializer.
  delete out.comments
  return out
}

export const list = () => fetchAll(`${path}/`)

export const get = id => client.get(`${path}/${id}/`).then(r => r.data)

export const save = recipe => upsert(path, toWritePayload(recipe))
