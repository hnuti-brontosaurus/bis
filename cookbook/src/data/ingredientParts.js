// Recipe ingredients are stored flat, each carrying its `part` name. The
// editor and the recipe page show them as rows interleaved with part
// headings instead, so moving an ingredient between parts is plain sorting.
// Symbol-keyed so the marker never survives JSON.stringify.
const PART_HEADING = Symbol("part_heading")

export const partHeading = (name = "") => ({ [PART_HEADING]: true, name })

export const isPartHeading = row => !!row?.[PART_HEADING]

export const withPartHeadings = ingredients =>
  ingredients.flatMap((ingredient, index) =>
    ingredient.part && ingredient.part !== ingredients[index - 1]?.part
      ? [partHeading(ingredient.part), ingredient]
      : [ingredient],
  )

export const withoutPartHeadings = rows => {
  let part = ""
  const ingredients = []
  rows.forEach(row => {
    if (isPartHeading(row)) part = row.name ?? ""
    else ingredients.push({ ...row, part, order: ingredients.length })
  })
  return ingredients
}

const partEnd = (rows, start) => {
  const next = rows.findIndex((row, index) => index > start && isPartHeading(row))
  return next === -1 ? rows.length : next
}

// A part travels with its ingredients, swapping places with the neighbouring
// part; ingredients above the first heading count as one unnamed part.
export const movePart = (rows, index, direction) => {
  const end = partEnd(rows, index)
  if (direction === "up") {
    if (index === 0) return
    const previous = Math.max(
      rows.findLastIndex((row, i) => i < index && isPartHeading(row)),
      0,
    )
    rows.splice(previous, 0, ...rows.splice(index, end - index))
  } else {
    if (end === rows.length) return
    const moved = rows.splice(index, end - index)
    rows.splice(partEnd(rows, index), 0, ...moved)
  }
}

// The ingredients above the first heading become the first part, so splitting
// a plain list keeps what the chef already wrote.
export const addPart = rows => {
  if (rows.length && !rows.some(isPartHeading)) rows.unshift(partHeading())
  rows.push(partHeading())
}
