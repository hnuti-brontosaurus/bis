// CommonJS so require() honours the NODE_PATH that pre-commit's node env sets;
// an ESM import would ignore it when eslint is installed outside nest_boxes/.
const js = require("@eslint/js")
const pluginVue = require("eslint-plugin-vue")
const skipFormatting = require("@vue/eslint-config-prettier/skip-formatting")
const unusedImports = require("eslint-plugin-unused-imports")
const globals = require("globals")

module.exports = [
  {
    ignores: [
      "dist/**",
      "dev-dist/**",
      "node_modules/**",
      "test-results/**",
      "playwright-report/**",
    ],
  },
  js.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  skipFormatting,
  {
    plugins: { "unused-imports": unusedImports },
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: { ...globals.browser },
    },
    rules: {
      "no-unused-vars": "off",
      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": [
        "error",
        { args: "after-used", argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "vue/multi-word-component-names": "off",
    },
  },
  {
    files: ["**/*.cjs"],
    languageOptions: { sourceType: "commonjs", globals: { ...globals.node } },
  },
  {
    files: ["**/e2e/**/*.js", "**/*.config.js"],
    languageOptions: { globals: { ...globals.node } },
  },
]
