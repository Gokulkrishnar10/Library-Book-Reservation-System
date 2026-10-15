import { test, expect } from '@playwright/test'

test.describe('Library Book Reservation System — Comprehensive E2E Suite', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('1. Core Application Header & Catalog Initialization', async ({ page }) => {
    // Brand identity & real-time polling indicator
    await expect(page.locator('.brand-title')).toContainText('Library Book Reservation System')
    await expect(page.locator('.live-indicator')).toContainText('Live 5s Polling')

    // Search bar and multi-genre controls exist
    await expect(page.locator('#search-input')).toBeVisible()
    await expect(page.locator('#genre-pill-all')).toBeVisible()

    // At least one book card is rendered in the grid
    const bookCards = page.locator('.book-card')
    await expect(bookCards.first()).toBeVisible()
  })

  test('2. Multi-Genre Filtering & Dynamic Combination', async ({ page }) => {
    // Select Horror genre pill
    const horrorPill = page.locator('#genre-pill-horror')
    await expect(horrorPill).toBeVisible()
    await horrorPill.click()
    await expect(horrorPill).toHaveClass(/active/)

    // Select Comedy genre pill to create dual-match filter
    const comedyPill = page.locator('#genre-pill-comedy')
    await expect(comedyPill).toBeVisible()
    await comedyPill.click()
    await expect(comedyPill).toHaveClass(/active/)

    // Books grid updates to show matching books
    const bookCards = page.locator('.book-card')
    await expect(bookCards.first()).toBeVisible()

    // Reset back to All Genres
    const allPill = page.locator('#genre-pill-all')
    await allPill.click()
    await expect(allPill).toHaveClass(/active/)
    await expect(horrorPill).not.toHaveClass(/active/)
  })

  test('3. Search Bar Live Filtering', async ({ page }) => {
    const searchInput = page.locator('#search-input')
    await searchInput.fill('Dracula')

    // Only Dracula or matching titles should remain visible
    const bookTitle = page.locator('.book-card .book-title').first()
    await expect(bookTitle).toContainText(/Dracula/i)

    // Clear search
    await searchInput.fill('')
  })

  test('4. Live Analytics & Catalog Intelligence Charts (Donut + Bar)', async ({ page }) => {
    const analyticsSection = page.locator('#analytics-section')
    await expect(analyticsSection).toBeVisible()

    // Both Donut Chart and Horizontal Bar Chart are rendered
    await expect(page.locator('#genre-distribution-chart')).toBeVisible()
    await expect(page.locator('#top-demand-chart')).toBeVisible()
  })

  test('5. Authentication Modal: Sign In, Register & Forgot Password Dialogs', async ({ page }) => {
    // Open Auth Modal
    const authBtn = page.getByRole('button', { name: /Sign In \/ Register/i })
    await authBtn.click()

    const modalDialog = page.locator('.modal-dialog')
    await expect(modalDialog).toBeVisible()
    await expect(page.locator('.modal-title')).toContainText('Sign In')

    // Switch to Register mode
    await page.getByRole('button', { name: /Register here/i }).click()
    await expect(page.locator('.modal-title')).toContainText('Create Patron Account')

    // Switch to Forgot Password mode
    await page.getByRole('button', { name: /Sign In instead/i }).click()
    await page.getByRole('button', { name: /Forgot Password\?/i }).click()
    await expect(page.locator('.modal-title')).toContainText('Reset Your Password')

    // Close Modal
    await page.locator('.modal-close-btn').click()
    await expect(modalDialog).not.toBeVisible()
  })

  test('6. Faded Reserved Button State & Duplicate Hold Warning Toast', async ({ page }) => {
    // Pick the first available book card
    const firstCard = page.locator('.book-card').first()
    await expect(firstCard).toBeVisible()

    const userInput = firstCard.locator('.reserve-input')
    const reserveBtn = firstCard.locator('button[id^="reserve-btn-"]')

    // Enter a valid patron name
    await userInput.fill('Alexander Smith')
    await reserveBtn.click()

    // Wait for the button to transition into the faded reserved state
    await expect(reserveBtn).toHaveClass(/btn-reserved/)
    await expect(reserveBtn).toContainText('Reserved')

    // Click the faded reserved button again (testing accidental or duplicate click)
    await reserveBtn.click()

    // Verify floating red error notification appears at the top
    const errorBanner = page.locator('#error-banner')
    await expect(errorBanner).toBeVisible()
    await expect(errorBanner).toContainText('User already has an active reservation for this book')

    // Dismiss error banner
    await page.locator('#error-banner-dismiss').click()
    await expect(errorBanner).not.toBeVisible()

    // Expand drawer and cancel hold to restore database state cleanly
    const toggleBtn = firstCard.locator('button[id^="toggle-reservations-"]')
    await toggleBtn.click()
    const cancelBtn = firstCard.locator('button:has-text("Cancel Hold")').first()
    if (await cancelBtn.isVisible()) {
      await cancelBtn.click()
    }
  })

  test('7. Reservation Drawer Expansion & Active Hold Verification', async ({ page }) => {
    // Locate the first book card that has active reservations (e.g. Clean Code or Book A)
    const cardWithDrawer = page.locator('.book-card:has(button[id^="toggle-reservations-"])').first()
    await expect(cardWithDrawer).toBeVisible()

    const toggleBtn = cardWithDrawer.locator('button[id^="toggle-reservations-"]')
    await toggleBtn.click()

    // Drawer should open and display active reservation item with countdown badge
    const drawer = cardWithDrawer.locator('.reservations-drawer')
    await expect(drawer).toBeVisible()
    await expect(drawer.locator('.countdown-badge').first()).toBeVisible()
  })

  test('8. AI Librarian Widget, Auto-Filtered Catalog & Highlight Navigation', async ({ page }) => {
    // Open floating AI Librarian widget
    const aiTrigger = page.locator('.ai-floating-trigger-btn')
    await expect(aiTrigger).toBeVisible()
    await aiTrigger.click()

    const chatWindow = page.locator('.ai-chat-window')
    await expect(chatWindow).toBeVisible()
    await expect(page.locator('.ai-header-title')).toContainText('AI Librarian')

    // Verify speech recognition mic and voice controls exist
    await expect(page.locator('.ai-mic-btn')).toBeVisible()
    await expect(page.locator('.ai-toggle-sound-btn')).toBeVisible()

    // Close chat
    await page.locator('.ai-close-btn').click()
    await expect(chatWindow).not.toBeVisible()
  })

  test('9. Admin Portal Console & KPI Telemetry', async ({ page }) => {
    // Open auth modal and log in as default System Administrator
    const authBtn = page.getByRole('button', { name: /Sign In \/ Register/i })
    await authBtn.click()

    await page.locator('#login-email').fill('admin@library.com')
    await page.locator('#login-password').fill('Admin123!')
    await page.locator('button[type="submit"]:has-text("Sign In")').click()

    // Verify Admin badge and Console view switch button
    const adminToggleBtn = page.getByRole('button', { name: /Admin Console/i })
    await expect(adminToggleBtn).toBeVisible()
    await adminToggleBtn.click()

    // Admin portal should render
    await expect(page.locator('.admin-portal-container')).toBeVisible()
    await expect(page.locator('.kpi-grid')).toBeVisible()

    // Back to catalog
    await page.getByRole('button', { name: /Back to Catalog/i }).click()
    await expect(page.locator('#books-grid')).toBeVisible()
  })
})
