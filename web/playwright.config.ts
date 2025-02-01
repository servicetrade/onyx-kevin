import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  globalSetup: require.resolve("./tests/e2e/global-setup"),
  timeout: 60000, // 60 seconds timeout
  projects: [
    {
      name: "admin",
      use: {
        ...devices["Desktop Chrome"],
        storageState: "admin_auth.json",
      },
      testIgnore: ["**/codeUtils.test.ts"],
    },
  ],
});
