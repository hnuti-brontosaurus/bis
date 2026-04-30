import { fetchAll } from "./client.js"

export const list = () => fetchAll("/recipe_tags/")
