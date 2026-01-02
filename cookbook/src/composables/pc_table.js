import { useLocalStorage, useThrottleFn } from "@vueuse/core"
import { h, onMounted } from "vue"
import axios from "axios"
import { useErrorHandler } from "@/contrib/composables/errorHandler.js"
import { NBadge, useDialog, useMessage } from "naive-ui"
import {
  faAdd,
  faClockRotateLeft,
  faEdit,
  faTrash,
} from "@fortawesome/free-solid-svg-icons"
import { useHelpers } from "@/contrib/composables/helpers.js"
import { useRender } from "@/contrib/composables/render.js"

const tables = {}
let fetch = {}

const fields = {
  aae_modules: ["name", "description"],
  magenta_allowed_rate_plans: ["name", "rateplan", "root_product"],
  postpaid_discounts: ["id", "name", "price"],
  premium_hw_rate_plans: ["id", "name"],
  rate_plan_price_catalogs: ["id", "name", "price"],
  rate_plans: ["id", "name", "excluded_services"],
  aae_transaction_types: ["transaction_type", "aae_modules"],
  additional_products: [
    "id",
    "name",
    "properties",
    "destination_type",
    "destination_code",
    "product_type",
    "product_value",
    "reference_product_id",
  ],
  ore_scenarios: [
    "id_scenario",
    "additional_attributes",
    "application_list",
    "description",
    "generate_documents",
    "installation_address_format_migration_to_optic",
    "order_reason",
    "ore_scenario",
    "priority",
    "product_code_list",
    "root_product_id_type",
    "tbui",
    "transaction_type_list",
    "create_bp_flag",
  ],
}

export function usePCTable(name) {
  const { handleAxiosError } = useErrorHandler()
  const message = useMessage()
  const dialog = useDialog()
  const { getIconColumn } = useHelpers()
  const { icon } = useRender()

  if (!(name in tables)) tables[name] = useLocalStorage(name, [])

  const data = tables[name]

  fetch[name] ??= useThrottleFn(() => {
    if (!(name in fields))
      throw `Unknown fields for ${name}, define them in pc_table.js`
    axios
      .post("/pc_table", {
        method: "all",
        message: `Getting ${name}`,
        table: name,
        fields: fields[name],
      })
      .then(result => (data.value = result.data.result))
      .catch(handleAxiosError(`Failed to fetch ${name}`))
  }, 1000)

  onMounted(fetch[name])

  const upsert = data =>
    axios
      .post("/pc_table", {
        method: "upsert",
        message: `Upserting ${name}`,
        table: name,
        data: data,
      })
      .then(() => message.success(`Saved`))
      .then(fetch[name])
      .catch(handleAxiosError(`Failed to upsert ${name}`))

  const dialog_remove = id_field => row => {
    const id = row[id_field]
    const d = dialog.warning({
      title: `Remove ${name}?`,
      content: `${name} ${id} will be removed`,
      positiveText: "Áno",
      negativeText: "Nie",
      onPositiveClick: () => {
        d.loading = true
        return remove({ [id_field]: id })
      },
    })
  }

  const remove = filter_by =>
    axios
      .post("/pc_table", {
        method: "delete",
        message: `Deleting ${name}`,
        table: name,
        filter_by,
      })
      .then(fetch[name])
      .then(() => message.success(`Deleted`))
      .catch(handleAxiosError(`Failed to remove ${name}`))

  const restore = to =>
    axios
      .post("/pc_table", {
        method: "delete",
        message: `Deleting all ${name}`,
        table: name,
        filters: { field: fields[name][0], op: "not_in", value: [] },
      })
      .then(() => upsert(to))
      .catch(handleAxiosError(`Failed to remove all ${name}`))

  const getIconColumns = (ref, id_field, history) => {
    return [
      getIconColumn(
        "_edit",
        row => (ref.value = row),
        icon(faEdit, "edit"),
        icon(faAdd, "add"),
      ),
      getIconColumn("_delete", dialog_remove(id_field), icon(faTrash, "remove"), () =>
        h(
          NBadge,
          { dot: true, show: !!history.value?.alert },
          icon(faClockRotateLeft, "show history"),
        ),
      ),
    ]
  }

  return {
    data,
    fetch: fetch[name],
    upsert,
    remove,
    dialog_remove,
    restore,
    getIconColumns,
  }
}
