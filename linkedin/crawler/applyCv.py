import asyncio
import json
from pyppeteer import launch
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(current_directory, '../cookies/linkedin_cookies.json')
PDF_PATH = "./cv/77264049-73f6-4600-bdcf-67b5de8f55a9.pdf"

async def load_cookies(page):
    try:
        with open(COOKIES_PATH, 'r') as f:
            cookies = json.load(f)
        await page.setCookie(*cookies)
        print("Cookies đã được tải thành công!")
    except FileNotFoundError:
        print("Không tìm thấy file cookies, cần đăng nhập lần đầu.")

async def click_if_exists(page, selector):
    """Click a button if it exists on the page."""
    button = await page.querySelector(selector)
    if button:
        await button.click()
        print(f"Đã ấn vào nút có class '{selector}'")
    else:
        print(f"Không tìm thấy nút với class '{selector}'")

async def upload_csv(page, selector):
    await page.waitForSelector(selector, {'timeout': 10000})
    file_input = await page.querySelector('input[type="file"]')
    await file_input.uploadFile(PDF_PATH)
    print(f"Tải lên file từ '{PDF_PATH}' thành công.")

    await next_action(page)

async def next_action(page):
    await page.waitForSelector('button.artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view', {'timeout': 10000})
    await page.click('button.artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view')

async def fill_inputs(page):
    input_elements = await page.querySelectorAll('input.artdeco-text-input--input')
    for input_element in input_elements:
        await input_element.focus()
        await input_element.click({'clickCount': 3})
        await input_element.press('Backspace')
        await input_element.type('5')
    print("Đã điền giá trị '3' vào tất cả các input.")

async def apply_to_job(url, browser):
    page = await browser.newPage()
    await page.setViewport({"width": 1920, "height": 1080})

    await load_cookies(page)

    await page.goto(url)
    if await page.querySelector('button.jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view') is not None:
        await page.waitForSelector('button.jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view', {'timeout': 10000})
        await asyncio.sleep(2)
        await page.click('button.jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view')
        print("Đã ấn vào nút 'Easy Apply' với lớp đầu tiên.")


    await page.waitForSelector('.artdeco-modal__content', {'timeout': 20000})
    print("Modal đã mở")

    await next_action(page)

    await upload_csv(page, "label.jobs-document-upload__upload-button.artdeco-button--secondary.artdeco-button--2.mt2")

    await asyncio.sleep(2)

    modal_selector = 'div.artdeco-modal.artdeco-modal--layer-default.jobs-easy-apply-modal'
    while await page.querySelector(modal_selector):
        await click_if_exists(page, 'button.artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--tertiary.ember-view')
        await fill_inputs(page)
        await next_action(page)
        await asyncio.sleep(2)

    print("Hoàn thành tất cả các bước và modal đã đóng.")

async def main():
    browser = await launch(headless=False)

    job_url = 'https://www.linkedin.com/jobs/search/?currentJobId=3899258490&distance=25&geoId=104195383&keywords=remote&origin=JOBS_HOME_SEARCH_CARDS'
    await apply_to_job(job_url, browser)

asyncio.run(main())
