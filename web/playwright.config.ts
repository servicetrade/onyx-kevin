import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  globalSetup: require.resolve("./tests/e2e/global-setup"),
  projects: [
    {
      name: "admin",
      use: {
        ...devices["Desktop Chrome"],
        storageState: "admin_auth.json",
        actionTimeout: 60000,
      },
      testIgnore: ["**/codeUtils.test.ts"],
    },
  ],
  use: {
    actionTimeout: 60000,
    navigationTimeout: 60000,
  },
  timeout: 60000,
});
