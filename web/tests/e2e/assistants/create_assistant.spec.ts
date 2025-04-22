import { test, expect } from "@chromatic-com/playwright";
import { dragElementAbove, dragElementBelow } from "../utils/dragUtils";
import { loginAsRandomUser } from "../utils/auth";

test("Assistant Creation and Edit Verification", async ({ page }) => {
  await page.context().clearCookies();
  await loginAsRandomUser(page);

  const assistantName = `Test Assistant ${Date.now()}`;
  const assistantDescription = "This is a test assistant description.";
  const assistantInstructions = "These are the test instructions.";

  // Navigate to the chat page
  await page.goto("http://localhost:3000/assistants/new");

  // Fill in assistant details
  await page.locator('input[name="name"]').fill(assistantName);
  await page.locator('input[name="description"]').fill(assistantDescription);
  await page
    .locator('textarea[name="system_prompt"]')
    .fill(assistantInstructions);

  // Submit the form
  await page.locator('button[type="submit"]').click();

  // Verify redirection to chat page with the new assistant ID
  await page.waitForURL(/.*\/chat\?assistantId=\d+.*/);
  const url = page.url();
  const assistantIdMatch = url.match(/assistantId=(\d+)/);
  expect(assistantIdMatch).toBeTruthy();
  const assistantId = assistantIdMatch ? assistantIdMatch[1] : null;
  expect(assistantId).not.toBeNull();

  await page.locator('button[aria-label="Explore Assistants"]').click();
  await page.waitForSelector('div[aria-label="Assistant Modal"]'); // Wait for modal to appear

  // Find the assistant card in the modal and scroll to it
  const modalContent = page.locator('div[aria-label="Assistant Modal"]');
  const modalBox = await modalContent.boundingBox();
  if (modalBox) {
    await page.mouse.move(
      modalBox.x + modalBox.width / 2,
      modalBox.y + modalBox.height / 2
    );
    await page.mouse.wheel(0, 500);
  }
  const assistantCard = page.locator(
    `//div[@aria-label="Assistant Modal"]//*[contains(text(), "${assistantName}") and not(contains(@class, 'invisible'))]`
  );
  await expect(assistantCard).toBeVisible();

  // Find and click the edit button within the card's scope
  // This selector might need adjustment based on the actual DOM structure
  const editButton = assistantCard.locator(
    'xpath=ancestor::*[contains(@class, "AssistantCard")]//button[contains(@aria-label, "Edit")]'
  );
  await editButton.click();

  // Verify we are on the edit page
  await page.waitForURL(`**/assistants/${assistantId}`);

  // Verify the fields have the original values
  await expect(page.locator('input[name="name"]')).toHaveValue(assistantName);
  await expect(page.locator('input[name="description"]')).toHaveValue(
    assistantDescription
  );
  await expect(page.locator('textarea[name="system_prompt"]')).toHaveValue(
    assistantInstructions
  );

  // Submit the edit form without changes
  await page.locator('button[type="submit"]:has-text("Update")').click();

  // Verify redirection back to the chat page
  await page.waitForURL(/.*\/chat\?assistantId=\d+.*/);
  expect(page.url()).toContain(`assistantId=${assistantId}`);
});
