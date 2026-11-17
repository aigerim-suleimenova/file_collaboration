/* eslint-env node */
module.exports = {
  root: true,
  env: { browser: true, es2022: true, node: true },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    '@vue/eslint-config-prettier',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  ignorePatterns: ['dist/', 'node_modules/'],
  overrides: [
    {
      // Route-level views are named after their route (Home, Login, ...); the
      // multi-word rule exists to avoid clashes with HTML elements in reusable
      // components, which does not apply to these.
      files: ['src/views/**/*.vue'],
      rules: { 'vue/multi-word-component-names': 'off' },
    },
  ],
}
