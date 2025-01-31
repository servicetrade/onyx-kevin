import { test, expect } from "@playwright/test";
import { loginAsRandomUser } from "../utils/auth";
import {
  navigateToAssistantInHistorySidebar,
  sendMessage,
  startNewChat,
  switchModel,
} from "../utils/chatActions";

test("Chat workflow", async ({ page }) => {
  await page.context().clearCookies();
  await loginAsRandomUser(page);

  // Initial setup
  await page.goto("http://localhost:3000/chat");
  // Interact with Art assistant
  await navigateToAssistantInHistorySidebar(
    page,
    "[-3]",
    "Assistant for generating"
  );
  await sendMessage(page, "Hi");

  await startNewChat(page);

  // Check for expected text
  // Log current text
  const currentText = await page
    .locator('div[data-testid="chat-intro"]')
    .textContent();
  console.log("Current text:", currentText);
  await expect(page.getByText("Assistant for generating")).toBeVisible();

  // Interact with General assistant
  await switchModel(page, "General");

  // Check URL after clicking General assistant
  await expect(page).toHaveURL("http://localhost:3000/chat?assistantId=-1", {
    timeout: 5000,
  });

  // Create a new assistant
  await page.getByRole("button", { name: "Explore Assistants" }).click();
  await page.getByRole("button", { name: "Create" }).click();
  await page.getByTestId("name").click();
  await page.getByTestId("name").fill("Test Assistant");
  await page.getByTestId("description").click();
  await page.getByTestId("description").fill("Test Assistant Description");
  await page.getByTestId("system_prompt").click();
  await page.getByTestId("system_prompt").fill("Test Assistant Instructions");
  await page.getByRole("button", { name: "Create" }).click();

  // Verify new assistant creation
  await expect(page.getByText("Test Assistant Description")).toBeVisible({
    timeout: 5000,
  });

  // Start another new chat
  await page.getByRole("link", { name: "Start New Chat" }).click();
  await expect(page.getByText("Assistant with access to")).toBeVisible({
    timeout: 5000,
  });
});
