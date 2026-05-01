// CommonJS so require() honours NODE_PATH set by pre-commit's node env.
// ESM `import` ignores NODE_PATH and would fail with ERR_MODULE_NOT_FOUND
// when this config is loaded by an eslint installed outside cookbook/.
const js = require("@eslint/js")
const pluginVue = require("eslint-plugin-vue")
const skipFormatting = require("@vue/eslint-config-prettier/skip-formatting")
const unusedImports = require("eslint-plugin-unused-imports")
const globals = require("globals")

module.exports = [
  {
    ignores: [
      "dist/**",
      "node_modules/**",
      "cypress/screenshots/**",
      "cypress/videos/**",
    ],
  },
  js.configs.recommended,
  ...pluginVue.configs["flat/essential"],
  skipFormatting,
  {
    files: ["**/cypress/**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
        cy: "readonly",
        Cypress: "readonly",
        expect: "readonly",
        describe: "readonly",
        it: "readonly",
        before: "readonly",
        beforeEach: "readonly",
        after: "readonly",
        afterEach: "readonly",
        context: "readonly",
        specify: "readonly",
      },
    },
  },
  {
    plugins: { "unused-imports": unusedImports },
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: { ...globals.browser, ...globals.node },
    },
    rules: {
      "no-unused-vars": "off",
      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": [
        "error",
        {
          args: "after-used",
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
    },
  },
]
