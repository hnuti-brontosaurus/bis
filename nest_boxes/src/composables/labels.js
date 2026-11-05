// The Czech names of the backend's choices (nest_boxes/models.py, categories).

const options = labels =>
  Object.entries(labels).map(([value, label]) => ({ value, label }))

export const STATUS_LABELS = {
  planned: "plánovaná",
  in_use: "vyvěšená",
  taken_down: "sundaná na opravu",
  missing: "nenalezená",
  ended: "zaniklá",
}

// `season_state` of a box, see NestBoxQuerySet.with_season_state
export const SEASON_STATE_LABELS = {
  to_check: "Ke kontrole",
  attention: "K opravě",
  done: "Hotovo",
  planned: "Plánovaná",
}

// The entries of the map legend, see LEGEND_KEYS in composables/filters.js
export const LEGEND_LABELS = {
  planned: "Plánované",
  to_check: "Ke kontrole",
  attention: "K opravě",
  done: "Hotovo",
  ended: "Zaniklé",
}

// Ending is an action of its own, never a plain edit.
export const EDITABLE_STATUSES = ["planned", "in_use", "taken_down", "missing"]

export const CONDITION_LABELS = {
  fine: "v pořádku",
  needs_repair: "potřebuje opravu",
  needs_replacing: "potřebuje vyměnit",
}

export const HOLE_SHAPE_LABELS = {
  round: "kulatý",
  oval: "oválný",
  slit: "štěrbina",
  open_front: "polobudka",
  other: "jiný",
}

// Only these have a width the type is told by.
export const MEASURED_HOLE_SHAPES = ["round", "oval"]

export const OPENING_LABELS = {
  front: "přední",
  roof: "horní",
  side: "boční",
  none: "neotevírá se",
}

export const MATERIAL_LABELS = {
  wood: "dřevo",
  wood_cement: "dřevocement",
  plastic: "plast",
  other: "jiný",
}

export const FOUND_LABELS = {
  found: "nalezena",
  not_found: "nenalezena",
  not_reached: "nedostali jsme se k ní",
}

export const CLEANING_LABELS = {
  cleaned: "vyčištěno",
  not_cleaned: "nevyčištěno",
}

// What the box held this season, see Check.Content
export const CONTENT_LABELS = {
  nothing: "prázdná",
  bird_nest: "hnízdo nebo zbytky po ptácích",
  other_animal: "jiné zvíře",
  unknown: "obsah nevím",
}

export const BOX_LEFT_LABELS = {
  fine: "v pořádku",
  needs_repair: "potřebuje opravu",
  needs_replacing: "potřebuje vyměnit",
  taken_down: "sundaná",
}

export const STATUS_OPTIONS = options(STATUS_LABELS)
export const CONDITION_OPTIONS = options(CONDITION_LABELS)
export const HOLE_SHAPE_OPTIONS = options(HOLE_SHAPE_LABELS)
export const OPENING_OPTIONS = options(OPENING_LABELS)
export const MATERIAL_OPTIONS = options(MATERIAL_LABELS)
export const BOX_LEFT_OPTIONS = options(BOX_LEFT_LABELS)

export const categoryOptions = items =>
  items.map(item => ({ value: item.id, label: item.name }))

export const byId = items => new Map(items.map(item => [item.id, item]))

// Shown while an article has no title of its own yet. Also the order of the
// help's table of contents.
export const HELP_TITLES = {
  cleaning_howto: "Jak vyčistit budku",
  occupants: "Co v budce bydlelo?",
  contents: "Co bylo uvnitř",
  type: "Typy budek",
  hole: "Měření otvoru",
  opening: "Otevírání budky",
  box_left: "Kdy budka potřebuje opravu",
  box_changes: "Co dělat, když se budka změnila",
  found: "Když budku nenajdeš",
  cleaning: "Kdy budku nečistit",
  hanging: "Věšení nové budky",
  about: "O databázi budek",
  sources: "Zdroje",
}

export const helpTitle = article => article.title || HELP_TITLES[article.slug]
