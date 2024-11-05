import asyncio
import json
from pyppeteer import launch
from dotenv import load_dotenv
import os

load_dotenv()

LINKEDIN_USERNAME = os.getenv('LINKEDIN_USERNAME')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

current_directory = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(current_directory, '../cookies/linkedin_cookies.json')

async def save_cookies(page):
    cookies = await page.cookies()
    with open(COOKIES_PATH, 'w') as f:
        json.dump(cookies, f)
    print("Cookies đã được lưu thành công!")

async def load_cookies(page):
    try:
        with open(COOKIES_PATH, 'r') as f:
            cookies = json.load(f)
        await page.setCookie(*cookies)
        print("Cookies đã được tải thành công!")
    except FileNotFoundError:
        print("Không tìm thấy file cookies, cần đăng nhập lần đầu.")


async def login():
    browser = await launch(headless=False)
    page = await browser.newPage()

    print("Load Login page")
    await page.goto("https://www.linkedin.com/login")
    await page.waitForSelector('body')

    await page.type("#username", LINKEDIN_USERNAME)
    await page.type("#password", LINKEDIN_PASSWORD)
    await page.click('button[type="submit"]')

    await page.waitForNavigation()

    await save_cookies(page)
    await browser.close()

asyncio.run(login())