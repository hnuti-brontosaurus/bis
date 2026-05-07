/**
 * ESLint rule: flag translation keys that aren't present in the YAML
 * source-of-truth (backend/translation/{string,model}_translations.yaml).
 *
 * Mirrors the Proxy lookup chain in src/composables/translations.js:
 *   1. model_translations[group].fields[key] (with implicit "class" / "plural")
 *   2. string_translations.cookbook[group][key]
 *   3. string_translations.cookbook.common[key]
 *   4. string_translations.generic[key]
 *
 * The rule degrades silently when the YAML files aren't reachable
 * (e.g. running yarn lint inside the cookbook container, which only
 * mounts cookbook/). Pre-commit lint runs from the host and sees them.
 */
const fs = require("fs")
const path = require("path")
const YAML = require("yaml")

const REPO_ROOT = path.resolve(__dirname, "..", "..")
const STRING_YAML = path.join(REPO_ROOT, "backend", "translation", "string_translations.yaml")
const MODEL_YAML = path.join(REPO_ROOT, "backend", "translation", "model_translations.yaml")

const BUILTIN_MODEL_KEYS = new Set(["class", "plural"])

let cachedDictionary = null
const loadDictionary = () => {
  if (cachedDictionary) return cachedDictionary
  cachedDictionary = { strings: {}, models: {}, available: false }
  try {
    cachedDictionary.strings = YAML.parse(fs.readFileSync(STRING_YAML, "utf8")) ?? {}
    cachedDictionary.models = YAML.parse(fs.readFileSync(MODEL_YAML, "utf8")) ?? {}
    cachedDictionary.available = true
  } catch {
    // YAMLs unreachable — leave dictionary empty and have hasTranslation
    // return true so the rule emits no warnings under degraded conditions.
  }
  return cachedDictionary
}

const hasTranslation = (group, key) => {
  const dictionary = loadDictionary()
  if (!dictionary.available) return true
  const model = dictionary.models?.[group]
  if (model) {
    if (BUILTIN_MODEL_KEYS.has(key)) return true
    if (model.fields?.[key] != null) return true
  }
  const cookbook = dictionary.strings?.cookbook ?? {}
  if (cookbook[group]?.[key] != null) return true
  if (cookbook.common?.[key] != null) return true
  if (dictionary.strings?.generic?.[key] != null) return true
  return false
}

// Match only the outermost MemberExpression of a chain rooted at `_`.
// Walks down collecting property names, then peels an optional leading
// `.value` (script-side computed unwrap) and treats the next two as
// (group, key). Anything deeper is property access on the result string
// and irrelevant to the lookup.
const extractGroupKey = node => {
  if (
    node.parent?.type === "MemberExpression" &&
    node.parent.object === node &&
    !node.parent.computed
  ) {
    return null
  }
  const properties = []
  let cursor = node
  while (cursor?.type === "MemberExpression" && !cursor.computed) {
    const propertyName = cursor.property?.name
    if (!propertyName) return null
    properties.unshift(propertyName)
    cursor = cursor.object
  }
  if (cursor?.type !== "Identifier" || cursor.name !== "_") return null
  if (properties[0] === "value") properties.shift()
  if (properties.length < 2) return null
  return { group: properties[0], key: properties[1] }
}

module.exports = {
  meta: {
    type: "problem",
    docs: { description: "Flag translation keys missing from the YAML sources." },
    schema: [],
    messages: {
      missing: 'Missing translation: "{{group}}.{{key}}"',
    },
  },
  create(context) {
    const check = node => {
      const result = extractGroupKey(node)
      if (!result) return
      if (hasTranslation(result.group, result.key)) return
      context.report({
        node,
        messageId: "missing",
        data: result,
      })
    }
    const visitor = { MemberExpression: check }
    // .vue templates: walk both the script and the template body. The
    // helper is only present when vue-eslint-parser is the active parser
    // (i.e. the file extension is .vue). ESLint 9 exposes parserServices
    // via sourceCode; older code paths used context.parserServices.
    const parserServices =
      context.sourceCode?.parserServices ?? context.parserServices
    const define = parserServices?.defineTemplateBodyVisitor
    if (typeof define === "function") {
      return define(visitor, visitor)
    }
    return visitor
  },
}
