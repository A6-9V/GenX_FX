from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Navigate to the provided URL
        page.goto("https://jules.google.com/task/4495779589251265423", wait_until="networkidle")

        # Expect the title to contain "GenX" to confirm the app has loaded
        expect(page).to_have_title("GenX FX Trading Platform", timeout=10000)

        # Take a screenshot for visual verification
        page.screenshot(path="jules-scratch/verification/verification.png")

        print("Frontend verification successful. Screenshot saved.")

    except Exception as e:
        print(f"An error occurred during verification: {e}")
        # Take a screenshot even on failure for debugging
        page.screenshot(path="jules-scratch/verification/verification_error.png")

    finally:
        # Clean up
        context.close()
        browser.close()

with sync_playwright() as playwright:
    run(playwright)