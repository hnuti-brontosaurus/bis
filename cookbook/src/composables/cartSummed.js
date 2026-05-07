import { computed } from "vue"
import { useCartStore } from "@/data/cart.js"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useUnitsStore } from "@/data/units.js"
import { convertAmount } from "@/data/unitConversion.js"

const baseSlugFor = ingredient =>
  ingredient?.state === "liquid" ? "milliliter" : "grams"

const promotedSlug = (slug, amount) => {
  if (slug === "grams" && amount >= 1000) return "kilograms"
  if (slug === "milliliter" && amount >= 1000) return "liter"
  return slug
}

export const useCartSummed = () => {
  const cart = useCartStore()
  const ingredients = useIngredientsStore()
  const units = useUnitsStore()

  const unitBySlug = computed(() => {
    const m = {}
    for (const u of units.list) m[u.slug] = u
    return m
  })

  const summed = computed(() => {
    const byId = new Map()

    for (const group of cart.items) {
      group.ingredients.forEach((entry, index) => {
        if (!byId.has(entry.ingredient_id)) {
          byId.set(entry.ingredient_id, {
            ingredient_id: entry.ingredient_id,
            sources: [],
          })
        }
        byId.get(entry.ingredient_id).sources.push({
          group_id: group.id,
          recipe_id: group.recipe_id,
          recipe_name: group.recipe_name,
          ingredient_index: index,
          amount: entry.amount,
          unit_id: entry.unit_id,
          bought: !!entry.bought,
        })
      })
    }

    return Array.from(byId.values()).map(({ ingredient_id, sources }) => {
      const ingredient = ingredients.byId[ingredient_id]
      const baseSlug = baseSlugFor(ingredient)
      const baseUnit = unitBySlug.value[baseSlug]

      const convertible = []
      const unconvertible = []
      let totalBase = 0

      for (const source of sources) {
        const sourceUnit = units.byId[source.unit_id]
        const inBase =
          ingredient && baseUnit && sourceUnit
            ? convertAmount(source.amount, sourceUnit, baseUnit, ingredient)
            : null
        if (inBase != null && Number.isFinite(inBase)) {
          const enriched = { ...source, base_amount: inBase }
          convertible.push(enriched)
          // Sum only what's still to buy — checked-off sources drop out of
          // the displayed total.
          if (!source.bought) totalBase += inBase
        } else {
          unconvertible.push(source)
        }
      }

      let defaultUnit = baseUnit
      let defaultAmount = totalBase
      if (convertible.length && baseUnit && ingredient) {
        const promoSlug = promotedSlug(baseSlug, totalBase)
        if (promoSlug !== baseSlug) {
          const promoUnit = unitBySlug.value[promoSlug]
          const promoAmount =
            promoUnit && convertAmount(totalBase, baseUnit, promoUnit, ingredient)
          if (promoAmount != null && Number.isFinite(promoAmount)) {
            defaultUnit = promoUnit
            defaultAmount = promoAmount
          }
        }
      }

      const allBought = sources.every(source => source.bought)

      return {
        ingredient_id,
        ingredient,
        sources,
        convertible,
        unconvertible,
        total_base_amount: totalBase,
        base_unit: baseUnit,
        default_unit: defaultUnit,
        default_amount: defaultAmount,
        bought: allBought,
      }
    })
  })

  const unboughtCount = computed(() => summed.value.filter(row => !row.bought).length)

  /**
   * Compute the displayed amount for a summed row given a chosen unit_id.
   * Returns null if conversion isn't possible (caller should fall back to
   * showing convertible part separately from unconvertibles).
   */
  const displayAmountInUnit = (row, unitId) => {
    if (!row.convertible.length || !row.base_unit || !row.ingredient) return null
    const target = units.byId[unitId]
    if (!target) return null
    return convertAmount(row.total_base_amount, row.base_unit, target, row.ingredient)
  }

  return { summed, unboughtCount, displayAmountInUnit }
}
