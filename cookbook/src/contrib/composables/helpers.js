import {Fragment, Comment, isVNode, toValue, computed} from "vue"

export function useHelpers() {
  const arrayAssign = (a, b) => a.splice(0, a.length, ...b)
  const arraySwitch = (array, value) =>
    array.includes(value) ? array.splice(array.indexOf(value), 1) : array.push(value)

  const objectClear = a => Object.keys(a).forEach(key => delete a[key])

  function toValueLabel(input, key_prefix = "", separator = ";") {
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

  function textFilter(value, array, get_choices = item => [item]) {
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

  const today = () => new Date().toISOString().split("T")[0]

  const sortedDict = data => {
    if (data == null) return data
    if (Array.isArray(data)) return data.map(item => sortedDict(item))
    if (typeof data === "object")
      return Object.fromEntries(
        Object.entries(data)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(value => sortedDict(value)),
      )
    return data
  }

  const renderCell = value => {
    if (value === true) return "yes"
    if (value === false) return "no"
    if (value === undefined) return "undefined"
    if (value === null) return "null"
    return value
  }

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

  const runOnSorterKey = (sorter, key_to_fn) => {
    key_to_fn[sorter.columnKey]?.()
  }


  const isEmptyVNode = (vnode) => {
    if (!isVNode(vnode)) return true

    // <!-- -->
    if (vnode.type === Comment) return true

    // Fragment with no meaningful children
    if (vnode.type === Fragment) {
      const children = vnode.children
      return !children || children.every(isEmptyVNode)
    }

    // Text node
    if (typeof vnode.children === 'string') {
      return vnode.children.trim() === ''
    }

    return false
  }

  const mapping = (getter, setter) => computed({get: getter, set: setter})

  return {
    arrayAssign,
    toValueLabel,
    textFilter,
    arraySwitch,
    objectClear,
    today,
    sortedDict,
    renderCell,
    getIconColumn,
    runOnSorterKey,
    isEmptyVNode,
    mapping,
  }
}
