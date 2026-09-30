$('#id_administration_unit').select2({
    theme: 'bootstrap-5'
})

const is_dark_theme = () => document.documentElement.dataset.bsTheme === "dark"

const original_tinymce_init = tinyMCE.init
tinyMCE.init = function (config) {
    config.content_style = `@import url("${EDITOR_CSS_URL}");`
    config.body_class = is_dark_theme() ? "dark" : ""
    return original_tinymce_init.call(this, config)
}

document.addEventListener("theme_change", () => {
    tinyMCE.get().forEach(editor => editor.getBody().classList.toggle("dark", is_dark_theme()))
})
