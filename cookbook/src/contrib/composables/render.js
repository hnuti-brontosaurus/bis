import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
import { h } from "vue"
import { RouterLink } from "vue-router"
import WithHint from "@/contrib/components/WithHint.vue"

export function useRender() {
  function icon(icon, hint) {
    return () =>
      h(WithHint, { hint, placement: "top" }, () => h(FontAwesomeIcon, { icon }))
  }

  function routerLink(name, path) {
    return () => h(RouterLink, { to: { name: path } }, () => name)
  }

  return { icon, routerLink }
}
