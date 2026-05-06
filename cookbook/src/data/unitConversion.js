/**
 * Unit conversion for recipe ingredients. All conversions go through grams
 * as the hub. An ingredient defines per-state conversion factors:
 *   - g_per_liter:   bridges weight ↔ volume
 *   - g_per_piece:   bridges weight ↔ pieces (the generic "piece" unit)
 *   - g_per_serving: bridges weight ↔ servings
 *
 * `state` ('solid' | 'liquid') marks the natural group that doesn't need
 * a bridge: solid is naturally weight, liquid is naturally volume. Within
 * a group, units convert directly (cup ↔ ml without g_per_liter).
 *
 * SPECIAL_UNIT_GRAMS pins a slug → grams factor for ingredient-specific
 * piece units (e.g. česnek → stroužek, palička). Those units only show up
 * for ingredients listed here.
 */

export const WEIGHT_GRAMS = {
  grams: 1,
  kilograms: 1000,
}

export const VOLUME_ML = {
  milliliter: 1,
  liter: 1000,
  pinch: 0.5,
  teaspoon: 5,
  tablespoon: 15,
  handful: 60,
  cup: 250,
}

export const SPECIAL_UNIT_GRAMS = {
  česnek: { clove: 5, bulb: 50 },
}

const naturalGroup = ingredient =>
  ingredient?.state === "liquid" ? "volume" : "weight"

const unitToGrams = (amount, unit, ingredient) => {
  if (!unit) return null
  switch (unit.of) {
    case "weight": {
      const factor = WEIGHT_GRAMS[unit.slug]
      return factor != null ? amount * factor : null
    }
    case "volume": {
      const ml = VOLUME_ML[unit.slug]
      if (ml == null || ingredient?.g_per_liter == null) return null
      return (amount * ml * ingredient.g_per_liter) / 1000
    }
    case "pieces": {
      const special = SPECIAL_UNIT_GRAMS[ingredient?.name]?.[unit.slug]
      if (special != null) return amount * special
      if (unit.slug === "piece" && ingredient?.g_per_piece != null) {
        return amount * ingredient.g_per_piece
      }
      return null
    }
    case "servings": {
      if (ingredient?.g_per_serving == null) return null
      return amount * ingredient.g_per_serving
    }
    default:
      return null
  }
}

const gramsToUnit = (grams, unit, ingredient) => {
  const oneUnitInGrams = unitToGrams(1, unit, ingredient)
  if (oneUnitInGrams == null || oneUnitInGrams === 0) return null
  return grams / oneUnitInGrams
}

/**
 * A unit is allowed for an ingredient iff a full conversion chain exists
 * between the ingredient's natural group and the unit's group, AND the
 * unit itself has a defined conversion to grams.
 *
 * Solid (natural=weight): natural→grams is free; the unit must reach grams.
 * Liquid (natural=volume): natural→grams needs g_per_liter — except when
 * the unit IS a volume unit, in which case the conversion stays inside
 * volume and skips grams entirely.
 */
export const isUnitAllowed = (unit, ingredient) => {
  if (!unit || !ingredient) return false
  const natural = naturalGroup(ingredient)
  if (unit.of === natural) {
    if (unit.of === "weight") return WEIGHT_GRAMS[unit.slug] != null
    if (unit.of === "volume") return VOLUME_ML[unit.slug] != null
  }
  if (natural === "volume" && ingredient.g_per_liter == null) return false
  return unitToGrams(1, unit, ingredient) != null
}

export const filterAllowedUnits = (units, ingredient) =>
  units.filter(u => isUnitAllowed(u, ingredient))

/**
 * Czech plural form selection. Each Unit row stores three nominative forms:
 *   name  — 1     (gram)
 *   name2 — 2..4  (gramy)
 *   name5 — 0, 5+, decimals (gramů)
 * Decimals fall through to name5 — the genitive plural is the conventional
 * reading for fractional quantities ("0.5 gramů").
 */
export const pluralizeUnit = (amount, unit) => {
  if (!unit) return ""
  if (amount == null || amount === 1) return unit.name
  if (Number.isInteger(amount) && amount >= 2 && amount <= 4) {
    return unit.name2 || unit.name
  }
  return unit.name5 || unit.name
}

/**
 * Convert `amount` from `fromUnit` to `toUnit` for the given ingredient.
 * Within weight or volume, conversion is direct (so liquid w/o g_per_liter
 * can still switch ml↔cup). Cross-group conversions go through grams and
 * return null if any leg is undefined.
 */
export const convertAmount = (amount, fromUnit, toUnit, ingredient) => {
  if (!fromUnit || !toUnit || amount == null) return null
  if (fromUnit.id === toUnit.id) return amount
  if (fromUnit.of === toUnit.of) {
    if (fromUnit.of === "weight") {
      return (amount * WEIGHT_GRAMS[fromUnit.slug]) / WEIGHT_GRAMS[toUnit.slug]
    }
    if (fromUnit.of === "volume") {
      return (amount * VOLUME_ML[fromUnit.slug]) / VOLUME_ML[toUnit.slug]
    }
  }
  const grams = unitToGrams(amount, fromUnit, ingredient)
  if (grams == null) return null
  return gramsToUnit(grams, toUnit, ingredient)
}
