// Optional JS-only baseline. Use a project's own framework/TS-aware config when present.
import js from "@eslint/js";

export default [
  {
    ignores: [
      "**/node_modules/**",
      "**/dist/**",
      "**/build/**",
      "**/originals/**",
    ],
  },
  {
    files: ["**/*.js", "**/*.mjs"],
    ...js.configs.recommended,
    languageOptions: { ecmaVersion: "latest", sourceType: "module" },
    rules: {
      ...js.configs.recommended.rules,
      camelcase: ["warn", { properties: "never", ignoreDestructuring: false }],
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
    },
  },
];
