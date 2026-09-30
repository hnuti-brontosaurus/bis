const theme_storage_key = "game_book_theme"

function apply_theme(theme) {
    document.documentElement.dataset.bsTheme = theme
    // bis/static/tinymce_dark_mode.js picks the editor skin from data-theme
    document.documentElement.dataset.theme = theme
}

function toggle_theme() {
    const theme = document.documentElement.dataset.bsTheme === "dark" ? "light" : "dark"
    localStorage.setItem(theme_storage_key, theme)
    apply_theme(theme)
    document.dispatchEvent(new Event("theme_change"))
}

apply_theme(
    localStorage.getItem(theme_storage_key)
    || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
)
