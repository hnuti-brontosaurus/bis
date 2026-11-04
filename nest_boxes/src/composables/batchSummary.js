import { distance } from "@/components/map/geometry.js"
import { isVerification, reportedState } from "@/composables/boxes.js"
import { BOX_LEFT_LABELS } from "@/composables/labels.js"

// A position moved by less is GPS noise, not a moved box.
export const MOVED_FAR = 15

const REPAIRS = ["needs_repair", "needs_replacing", "taken_down"]
const OCCUPIED = ["bird_nest", "other_animal"]
const INSPECTED = ["nothing", ...OCCUPIED]

const changedKeys = check => Object.keys(check.box_changes)

const isInspected = check =>
  check.found === "found" &&
  check.cleaning !== "could_not_open" &&
  check.contents.some(content => INSPECTED.includes(content))

/** The batch page's tiles, from the batch's checks and the boxes volunteers added. */
export const batchTiles = (batch, checks, newBoxes) => {
  const inspected = checks.filter(isInspected)
  const count = filter => checks.filter(filter).length
  return [
    { value: checks.length, label: `z ${batch.box_count} zkontrolováno` },
    {
      value: count(check => reportedState(check) === "attention"),
      label: "potřebuje pozornost",
      tone: "warn",
    },
    { value: count(check => check.found === "found"), label: "nalezeno" },
    { value: count(check => check.cleaning === "cleaned"), label: "vyčištěno" },
    {
      value: inspected.filter(check =>
        check.contents.some(content => OCCUPIED.includes(content)),
      ).length,
      label: `obsazeno z ${inspected.length}`,
    },
    {
      value: count(check => REPAIRS.includes(check.box_left)),
      label: "oprava nebo výměna",
      tone: "warn",
    },
    {
      value: count(check => check.found === "not_found"),
      label: "nenalezeno",
      tone: "bad",
    },
    { value: newBoxes.length, label: "nových budek" },
    { value: count(check => isVerification(check.box_changes)), label: "ověřeno" },
    {
      value: count(
        check => changedKeys(check).length && !isVerification(check.box_changes),
      ),
      label: "změna budky",
    },
    { value: count(check => check.photos.length), label: "s fotkou" },
  ]
}

/**
 * What a manager should look at before confirming: [{check?, box, tone, title, detail}].
 * `boxesById` holds the area's boxes as they are now, before the batch applies.
 */
export const batchHighlights = (checks, newBoxes, { boxesById, typesById }) => [
  ...newBoxes.map(box => ({
    key: `box-${box.id}`,
    box,
    tone: "info",
    title: "Nová budka",
    detail: "přidal ji dobrovolník, potvrdí se s obchůzkou",
  })),
  ...checks.flatMap(check => {
    const box = boxesById.get(check.box_id)
    const items = []
    const add = (tone, title, detail) =>
      items.push({ key: `${check.id}-${title}`, check, box, tone, title, detail })
    if (check.found === "not_found") add("bad", "Nenalezena", check.note)
    if (REPAIRS.includes(check.box_left))
      add("warn", BOX_LEFT_LABELS[check.box_left], check.note)
    const changes = check.box_changes
    if ("type" in changes && changes.type !== box.type_id)
      add(
        "info",
        "Typ změněn",
        `${typesById.get(box.type_id)?.name ?? "neznámý"} → ${typesById.get(changes.type)?.name ?? "neznámý"}`,
      )
    if (changes.location && !changes.hung) {
      const moved = distance(box.location, changes.location)
      if (moved >= MOVED_FAR)
        add(
          "info",
          `Poloha posunuta o ${Math.round(moved)} m`,
          "nová poloha z telefonu",
        )
    }
    if (changes.hung) add("info", "Pověšena", "plánovaná budka visí")
    return items
  }),
]
