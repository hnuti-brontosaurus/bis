const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const a = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

add_icon = (el, name) => {
    el.classList.remove("spinner-border")
    el.classList.remove("spinner-border-sm")
    el.classList.add(`bi`)
    el.classList.add(`bi-${name}`)
}
remove_icon = (el, name) => {
    el.classList.add("spinner-border")
    el.classList.add("spinner-border-sm")
    el.classList.remove(`bi`)
    el.classList.remove(`bi-${name}`)
    el.classList.remove(`bi-${name}-fill`)
}
state_to_icon = {
    favourites: 'star',
    is_verified: 'patch-check',
    thumbs_up: 'hand-thumbs-up',
    watchers: 'eye',
}

function toggle_state(event, el, game_id, state) {
    event.stopPropagation()
    el = el.children[0]
    let icon = state_to_icon[state]
    remove_icon(el, icon)

    axios
        .post(`/game_book/game/${game_id}/toggle/${state}/`, {}, {headers: {'X-CSRFToken': CSRF_TOKEN}})
        .then(({data}) => add_icon(el, icon + (data.on ? '-fill' : '')))
        .catch((error) => add_icon(el, "exclamation-lg"))
}
function add_form(el) {
    let form = el.parentElement
    let info_el = form.querySelector("[name$='TOTAL_FORMS']")
    let type = info_el.name.split('-')[0]
    let total = info_el.value

    let els = Array.from(form.querySelectorAll(`form > [name^=${type}-${total-1}-]`))
    els = [els[0].previousElementSibling, els[0], els[1]]
    let new_els = $(els).clone(true)

    new_els.find(':input').addBack(':input').each(function() {
        let name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-')
        let id = 'id_' + name
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked')
    })
    new_els.find('label').addBack('label').each(function() {
        let newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-')
        $(this).attr('for', newFor)
    })
    $('#id_' + type + '-TOTAL_FORMS').val(++total)
    $(els.at(-1)).after(new_els)
}
