import { test, expect } from "@playwright/test";
import { dragElementAbove, dragElementBelow } from "../utils/dragUtils";
import { loginAsRandomUser } from "../utils/auth";

test("Assistant Drag and Drop", async ({ page }) => {
  await page.context().clearCookies();
  await loginAsRandomUser(page);

  // Navigate to the chat page
  await page.goto("http://localhost:3000/chat");

  // Helper function to get the current order of assistants
  const getAssistantOrder = async () => {
    const assistants = await page.$$('[data-testid^="assistant-["]');
    return Promise.all(
      assistants.map(async (assistant) => {
        const nameElement = await assistant.$("p");
        return nameElement ? nameElement.textContent() : "";
      })
    );
  };

  // Get the initial order
  const initialOrder = await getAssistantOrder();

  // --- DRAG #1: Drag the second assistant (index 1) to where the first assistant (index 0) is
  const secondAssistant = page.locator('[data-testid^="assistant-["]').nth(1);
  const firstAssistant = page.locator('[data-testid^="assistant-["]').nth(0);

  await dragElementAbove(secondAssistant, firstAssistant, page);

  // Verify the new order
  const orderAfterDragUp = await getAssistantOrder();
  expect(orderAfterDragUp[0]).toBe(initialOrder[1]);
  expect(orderAfterDragUp[1]).toBe(initialOrder[0]);

  // --- DRAG #2: Drag the last assistant to the second position
  const assistants = page.locator('[data-testid^="assistant-["]');
  const lastIndex = (await assistants.count()) - 1;
  const lastAssistant = assistants.nth(lastIndex);
  const secondPosition = assistants.nth(1);

  // Add a 3 second timeout before dragging
  await page.waitForTimeout(3000);
  await dragElementBelow(lastAssistant, secondPosition, page);

  // Verify the new order
  const orderAfterDragDown = await getAssistantOrder();
  // The last pinned item should now end up at index 1
  expect(orderAfterDragDown[1]).toBe(initialOrder[lastIndex]);

  // Refresh the page
  await page.reload();

  // Verify the order is preserved after refresh
  const orderAfterRefresh = await getAssistantOrder();
  expect(orderAfterRefresh).toEqual(orderAfterDragDown);
});
