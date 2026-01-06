import { Fragment, Comment, isVNode, toValue, computed, unref } from "vue"

export function toValueLabel(input, key_prefix = "", separator = ";") {
  input = toValue(input)
  if (input == null) return []
  if (input?.[0]?.label) return input
  if (typeof input === "object" && !Array.isArray(input)) input = Object.keys(input)
  if (key_prefix) key_prefix += separator
  input = Array.from(new Set(input))
  return input.map(item => ({
    value: `${key_prefix}${item}`,
    key: `${key_prefix}${item}`,
    label: item,
  }))
}

export function textFilter(value, array, get_choices = item => [item]) {
  if (!value) return array

  let tokens = value
    .toLowerCase()
    .split(" ")
    .map(token => token.trim())
    .filter(token => !!token)

  if (!tokens.length) return array

  return array.filter(item =>
    tokens.every(token =>
      get_choices(item).some(choice =>
        JSON.stringify(choice)?.toLowerCase().includes(token),
      ),
    ),
  )
}

export const today = () => new Date().toISOString().split("T")[0]

const getIconColumn = (key, fn, row, header) => {
  return {
    key,
    render: row,
    fixed: "left",
    width: 31,
    sorter: !!header,
    renderSorter: header ? function () {} : undefined,
    title: header,
    cellProps: rowData => ({
      style: { cursor: "pointer", textAlign: "center" },
      onClick: () => fn(rowData),
    }),
  }
}

export const isEmptyVNode = vnode => {
  if (!isVNode(vnode)) return true

  // <!-- -->
  if (vnode.type === Comment) return true

  // Fragment with no meaningful children
  if (vnode.type === Fragment) {
    const children = vnode.children
    return !children || children.every(isEmptyVNode)
  }

  // Text node
  if (typeof vnode.children === "string") {
    return vnode.children.trim() === ""
  }

  return false
}

export const mapping = (get, set) => computed({ get, set })

export const propertyRef = (item, prop) =>
  mapping(
    () => unref(item)[prop],
    value => (unref(item)[prop] = value),
  )
