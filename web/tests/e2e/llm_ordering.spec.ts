import { test, expect } from "@playwright/test";

// Use pre-signed in "admin" storage state
test.use({
  storageState: "admin_auth.json",
});

test("test", async ({ page }) => {
  // Navigate to the chat page
  await page.goto("http://localhost:3000/chat");

  // Wait for the page to load
  await page.waitForSelector("#onyx-chat-input-textarea");

  // Verify that we're on the chat page
  await expect(page.url()).toBe("http://localhost:3000/chat");
  // User Settings Configuration
  await page.locator("#onyx-user-dropdown").click();
  await page.getByText("User Settings").click();
  await page.getByRole("combobox").click();
  await page.getByLabel("GPT 4 Turbo", { exact: true }).click();
  await page.getByLabel("Close modal").click();
  await expect(page.locator("#onyx-chat-input")).toContainText("GPT 4 Turbo");

  // Interacting with Art Assistant
  await page.getByTestId("assistant-[-3]").click();
  await page.locator("#onyx-chat-input-textarea").click();
  await page.locator("#onyx-chat-input-textarea").fill("Sample messae");
  await page.locator("#onyx-chat-input-send-button").click();

  // Wait for 4 seconds
  await page.waitForTimeout(4000);

  await expect(page.locator("#onyx-chat-input")).toContainText("GPT 4o");

  // Sending another message to Art Assistant
  await page.locator("#onyx-chat-input-textarea").click();
  await page.locator("#onyx-chat-input-textarea").fill("Sample message");
  await page.locator("#onyx-chat-input-send-button").click();

  // Starting new chats and verifying model changes
  await page.getByRole("link", { name: "Start New Chat" }).click();
  await expect(page.locator("#onyx-chat-input")).toContainText("GPT 4o");
  await page.getByRole("link", { name: "Start New Chat" }).click();
  await expect(page.locator("#onyx-chat-input")).toContainText("GPT 4 Turbo");

  // Switching between different AI models
  await page.getByRole("button", { name: "Logo GPT 4 Turbo" }).nth(1).click();
  await page.getByRole("button", { name: "Logo O1 Mini" }).click();

  // Interacting with Search Assistant
  await page.locator("#onyx-chat-input-textarea").click();
  await page.locator("#onyx-chat-input-textarea").fill("Sample message");
  await page.locator("#onyx-chat-input-send-button").click();

  // Navigating to a specific chat and verifying model
  await page.waitForSelector("#onyx-ai-message");

  await expect(page.locator("#onyx-chat-input")).toContainText("O1 Mini");

  // Creating a new custom assistant
  await page.getByRole("button", { name: "Explore Assistants" }).click();
  await page.getByRole("button", { name: "Create" }).click();
  await page.getByTestId("name").click();
  await page.getByTestId("name").fill("Sample Name");
  await page.getByTestId("description").click();
  await page.getByTestId("description").fill("Sample Description");
  await page.getByTestId("system_prompt").click();
  await page.getByTestId("system_prompt").fill("Sample Instructions");
  await page.getByRole("combobox").click();
  await page
    .getByLabel("GPT 4 Turbo (Preview)")
    .getByText("GPT 4 Turbo (Preview)")
    .click();
  await page.getByRole("button", { name: "Create" }).click();

  // Verifying and interacting with the new custom assistant
  await page.locator("#onyx-chat-input-textarea").fill("");
  await expect(page.locator("#onyx-chat-input")).toContainText(
    "GPT 4 Turbo (Preview)"
  );
  await page.locator("#onyx-chat-input-textarea").click();
  await page.locator("#onyx-chat-input-textarea").fill("Sample message");
  await page.locator("#onyx-chat-input-send-button").click();
  await expect(page.locator("#onyx-chat-input")).toContainText(
    "GPT 4 Turbo (Preview)"
  );

  // Switching back to Art Assistant and verifying model
  await page.getByText("ArtArt").click();
  await expect(page.locator("#onyx-chat-input")).toContainText("GPT 4o");
});
