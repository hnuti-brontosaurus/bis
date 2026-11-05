import { h } from "vue"
import { useDialog } from "naive-ui"
import { _ } from "@/composables/translations.js"

// A copy of someone else's recipe may go public only once it is the chef's
// own version; nothing checks that, so the chef is reminded at both steps.
const copyRules = intro => () =>
  h("div", [
    h("p", intro),
    h("ul", [
      h("li", _.value.recipes.copy_rule_photos),
      h("li", _.value.recipes.copy_rule_differs),
      h("li", _.value.recipes.copy_rule_source),
    ]),
  ])

export const useCopyRules = () => {
  const dialog = useDialog()

  const confirmDuplicate = onConfirm =>
    dialog.info({
      title: _.value.recipes.duplicate_title,
      content: copyRules(_.value.recipes.duplicate_intro),
      positiveText: _.value.recipes.duplicate,
      negativeText: _.value.common.back,
      onPositiveClick: onConfirm,
    })

  // Resolves whether to go on with publishing `recipe`.
  const confirmPublish = recipe =>
    new Promise(resolve => {
      if (!recipe.original_id) return resolve(true)
      dialog.warning({
        title: _.value.recipes.publish_copy_title,
        content: copyRules(_.value.recipes.publish_copy_intro),
        positiveText: _.value.recipes.publish,
        negativeText: _.value.common.back,
        onPositiveClick: () => resolve(true),
        onNegativeClick: () => resolve(false),
        onClose: () => resolve(false),
        onMaskClick: () => resolve(false),
      })
    })

  return { confirmDuplicate, confirmPublish }
}
