import { faEdit } from "@fortawesome/free-solid-svg-icons"
import router from "@/router.js"
import { useHelpers } from "@/contrib/composables/helpers.js"
import { useLocalStorage } from "@vueuse/core"
import { useSegmentations } from "@/composables/segmentations.js"
import { useRender } from "@/contrib/composables/render.js"

const selectedColumns = useLocalStorage("actions_columns", [
  { key: "action_master_id" },
  { key: "action_code" },
  { key: "action_name" },
])

const form = useLocalStorage("actions_form", {})

export function useActions() {
  const segmentations = useSegmentations()
  const { getIconColumn } = useHelpers()
  const { icon } = useRender()

  const columns = [
    { type: "selection", fixed: "left" },
    getIconColumn(
      "_edit",
      row => router.push(`/edit-actions/${row.action_master_id}`),
      icon(faEdit, "edit"),
    ),
    { title: "A2O?", key: "a2o_flag" },
    { title: "Category", key: "action_category" },
    { title: "Code", key: "action_code" },
    { title: "End date", key: "action_end_date" },
    { title: "Description", key: "action_long_description" },
    { title: "ID", key: "action_master_id" },
    { title: "Name", key: "action_name" },
    { title: "Name for channels", key: "action_name_for_channels" },
    {
      title: "Products",
      key: "action_products",
      render: row => JSON.stringify(row.action_products, null, 1),
      sorter: false,
    },
    { title: "Score", key: "action_score" },
    { title: "Start date", key: "action_start_date" },
    { title: "Audience", key: "audience_name" },
    { title: "Base?", key: "base_action_flag" },
    { title: "Bundled?", key: "bundled_flag" },
    { title: "Contact policy", key: "contact_policy_name" },
    { title: "Fully defined?", key: "fully_defined_flag" },
    { title: "Product HW?", key: "hw_flag" },
    { title: "Only digital?", key: "only_digital_flag" },
    { title: "Product url", key: "product_url" },
    { title: "Catalog code", key: "catalog_code" },
    { title: "Ref. ID", key: "reference_action_master_id" },
    { title: "Skip fee?", key: "skip_fee_flag" },
    { title: "Skip penalty?", key: "skip_penalty_flag" },
    { title: "Transaction type", key: "transaction_type_name" },
  ]
  columns.forEach(column => (column.sorter ??= "default"))

  const fulltextSearchFields = [
    { key: "contact_policy_name", force_op: "ilike" },
    { key: "action_master_id", validator: token => Number.isInteger(Number(token)) },
    { key: "action_code" },
    { key: "action_name" },
    { key: "audience_name" },
    { key: "transaction_type_name", force_op: "ilike" },
  ]

  const filtersMap = {
    application_name: { model: "Channel", op: "ilike", through: "ActionChannel" },
    channel_name: { model: "Channel", op: "ilike", through: "ActionChannel" },
    subtype: {
      model: "Subtype",
      op: "ilike",
      field: "name",
      through: ["ActionChannel", "ActionChannelSubtype"],
    },
    action_master_id: { model: "Action", op: "==" },
    action_code: { model: "Action", op: "ilike" },
    action_name: { model: "Action", op: "ilike" },
    audience_name: { model: "Action", op: "ilike" },
    contact_policy_name: { model: "Action", op: "==" },
    transaction_type_name: { model: "Action", op: "==" },
    action_score_from: { model: "Action", op: ">=", field: "action_score" },
    action_score_to: { model: "Action", op: "<=", field: "action_score" },
    action_start_date_since: { model: "Action", op: ">=", field: "action_start_date" },
    action_start_date_till: { model: "Action", op: "<=", field: "action_start_date" },
    action_end_date_since: { model: "Action", op: ">=", field: "action_end_date" },
    action_end_date_till: { model: "Action", op: "<=", field: "action_end_date" },
    a2o_flag: { model: "Action", op: "==" },
    bundled_flag: { model: "Action", op: "==" },
    fully_defined_flag: { model: "Action", op: "==" },
    hw_flag: { model: "Action", op: "==" },
    only_digital_flag: { model: "Action", op: "==" },
    skip_fee_flag: { model: "Action", op: "==" },
    skip_penalty_flag: { model: "Action", op: "==" },
    segmentation: {
      model: "Segmentation",
      op: "==",
      field: "segmentation_name",
      through: "Product",
    },
    eligibility_segmentation: {
      model: "Action",
      op: "json_like",
      field: "eligibilities",
    },
  }

  const setSegmentationIds = action => {
    const source = segmentations.data.value[action.audience_name]

    const getSegmentationIdForName = name => {
      if (!name) return null
      const id = source[name]?.segmentation_id
      if (!id) throw `Unknown segmentation name ${name}`
      return id
    }

    const getSegmentIdForName = (segmentation, name) => {
      if (!name) return null
      const id = source[segmentation]?.segments[name]?.segment_id
      if (!id) throw `Unknown segment name ${name} of segmentation ${segmentation}`
      return id
    }

    const setSegmentationIdsForProducts = products =>
      products.forEach(product => {
        product.segmentation_id = getSegmentationIdForName(
          product.segmentation?.segmentation_name,
        )
        product.segment_id = getSegmentIdForName(
          product.segmentation?.segmentation_name,
          product.segment?.segment_name,
        )
        setSegmentationIdsForProducts(product.children ?? [])
      })

    const setSegmentationIdsForEligibilityValue = value => {
      if (value.operator) value.operands.forEach(setSegmentationIdsForEligibilityValue)
      else {
        value.segmentation_id = getSegmentationIdForName(value.segmentation_name)
        value.segment_id = getSegmentIdForName(
          value.segmentation_name,
          value.segment_name,
        )
      }
    }

    setSegmentationIdsForProducts(action.action_products)
    Object.values(action.eligibilities)
      .flatMap(group => Object.values(group))
      .forEach(setSegmentationIdsForEligibilityValue)
  }

  return {
    fetch,
    columns,
    fulltextSearchFields,
    filtersMap,
    setSegmentationIds,
    selectedColumns,
    form,
  }
}
