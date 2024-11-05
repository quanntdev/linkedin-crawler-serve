import asyncio
import json
from pyppeteer import launch
from dotenv import load_dotenv
import os

async def login():
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    try:
        page = await browser.newPage()
        await page.setViewport({"width": 1280, "height": 800})
        print("Loading Login page")
        await page.goto("https://www.linkedin.com/login", timeout=60000)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        await browser.close()
        print("Done job")

asyncio.run(login())
