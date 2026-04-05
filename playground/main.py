import asyncio
from pathlib import Path

from linkedin_scraper import (
    BrowserManager,
    PersonScraper,
    RateLimitError,
    ScrapingError,
)

SESSION_FILE = Path(__file__).resolve().parent / "session.json"
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"


async def setup_session() -> bool:
    """Open browser for manual LinkedIn login; save session to SESSION_FILE. Returns True if saved."""
    print("No session file found. Opening browser for LinkedIn login...")
    print("Log in in the browser window, then return here and press Enter.")
    async with BrowserManager(headless=False) as browser:
        await browser.page.goto(LINKEDIN_LOGIN_URL, wait_until="domcontentloaded")
        input("Press Enter after you have logged in in the browser: ")
        await browser.save_session(str(SESSION_FILE))
    print(f"Session saved to {SESSION_FILE}. You can run the scraper next.")
    return True


async def main():
    if not SESSION_FILE.exists():
        await setup_session()
        return

    async with BrowserManager(headless=False) as browser:
        await browser.load_session(str(SESSION_FILE))
        await asyncio.sleep(2)
        scraper = PersonScraper(browser.page)
        try:
            person = await scraper.scrape("https://www.linkedin.com/in/nishantsh20/")
            print(f"Name: {person.name}")
            print(f"Headline: {person.headline}")
            print(f"Location: {person.location}")
            print(f"Experiences: {len(person.experiences)}")
            print(f"Education: {len(person.educations)}")
        except RateLimitError as e:
            wait_mins = getattr(e, "suggested_wait_time", 30) // 60
            print(f"LinkedIn rate limit: {e}")
            print(f"Wait ~{wait_mins} minutes and try again, or use the site less often.")
        except ScrapingError as e:
            if "rate limit" in str(e).lower():
                print("LinkedIn is blocking this request (often on first run when it detects automation).")
                print("A visible browser was used to reduce this. Wait a while and try again.")
            else:
                print(f"Scraping failed: {e}")


asyncio.run(main())