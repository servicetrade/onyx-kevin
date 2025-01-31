import { test, expect } from "@playwright/test";
import { loginAsRandomUser } from "../utils/auth";
import {
  navigateToAssistantInHistorySidebar,
  sendMessage,
  verifyCurrentModel,
  switchModel,
  startNewChat,
} from "../utils/chatActions";

test("test", async ({ page }) => {
  await page.context().clearCookies();
  await loginAsRandomUser(page);

  // Navigate to the chat page
  await page.goto("http://localhost:3000/chat");
  await page.waitForSelector("#onyx-chat-input-textarea");
  await expect(page.url()).toBe("http://localhost:3000/chat");

  // User Settings Configuration
  await page.locator("#onyx-user-dropdown").click();
  await page.getByText("User Settings").click();
  await page.getByRole("combobox").click();
  await page.getByLabel("GPT 4 Turbo", { exact: true }).click();
  await page.getByLabel("Close modal").click();
  await verifyCurrentModel(page, "GPT 4 Turbo");

  // Interacting with Art Assistant
  await navigateToAssistantInHistorySidebar(
    page,
    "[-3]",
    "Assistant for generating"
  );
  await sendMessage(page, "Sample message");
  await verifyCurrentModel(page, "GPT 4o");

  // Sending another message to Art Assistant
  await sendMessage(page, "Sample message");

  // Starting new chats and verifying model changes
  await startNewChat(page);
  await expect(page.getByText("Assistant for generating")).toBeVisible();

  await verifyCurrentModel(page, "GPT 4o");

  // Switching to GPT 4 Turbo
  await startNewChat(page);
  await verifyCurrentModel(page, "GPT 4 Turbo");

  // Switching to O1 Mini
  await switchModel(page, "O1 Mini");
  await sendMessage(page, "Sample message");
  await verifyCurrentModel(page, "O1 Mini");

  // Creating a new custom assistant
  await page.getByRole("button", { name: "Explore Assistants" }).click();
  await page.getByRole("button", { name: "Create" }).click();
  await page.waitForTimeout(2000);
  await page.getByTestId("name").fill("Sample Name");
  await page.getByTestId("description").fill("Sample Description");
  await page.getByTestId("system_prompt").fill("Sample Instructions");
  await page.getByRole("combobox").click();
  await page
    .getByLabel("GPT 4 Turbo (Preview)")
    .getByText("GPT 4 Turbo (Preview)")
    .click();
  await page.getByRole("button", { name: "Create" }).click();

  // Verifying and interacting with the new custom assistant
  await page.locator("#onyx-chat-input-textarea").fill("");
  await verifyCurrentModel(page, "GPT 4 Turbo (Preview)");
  await sendMessage(page, "Sample message");
  await verifyCurrentModel(page, "GPT 4 Turbo (Preview)");

  // Switching back to Art Assistant and verifying model
  await navigateToAssistantInHistorySidebar(
    page,
    "[-3]",
    "Assistant for generating"
  );
  await verifyCurrentModel(page, "GPT 4o");
});
