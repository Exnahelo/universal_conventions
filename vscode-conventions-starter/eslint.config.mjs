import js from "@eslint/js";

export default [
  js.configs.recommended,
  {
    files: ["**/*.js", "**/*.jsx"],
    ignores: ["node_modules/**", "dist/**", "build/**"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module"
    },
    rules: {
      "camelcase": ["error", { "properties": "never", "ignoreDestructuring": false }],
      "no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }]
    }
  }
];
