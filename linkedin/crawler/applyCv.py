import asyncio
import json
from pyppeteer import launch
import os
import uuid
from helper.response import Success, Error

class LinkedInJobApplicationService:
    def __init__(self):
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.COOKIE_PATH = os.path.join(self.current_directory, '../cookies/linkedin_cookies.json')
        self.CAPTURE_PATH = "./capture"

    async def load_cookies(self, page):
        try:
            with open(self.COOKIE_PATH, 'r') as f:
                cookies = json.load(f)
            await page.setCookie(*cookies)
            print("Cookies loaded successfully!")
        except FileNotFoundError:
            print("Cookie file not found, login may be required.")

    async def click_if_exists(self, page, selector):
        button = await page.querySelector(selector)
        if button:
            is_enabled = await page.evaluate(
                '(button) => button && !button.disabled && button.offsetParent !== null', button
            )
            if is_enabled:
                await button.click()
                print(f"Clicked on button with class '{selector}'")
            else:
                print(f"Button with class '{selector}' is not clickable.")
        else:
            print(f"Button with class '{selector}' not found.")

    async def upload_csv(self, page, selector, pdf_path):
        await page.waitForSelector(selector, {'timeout': 10000})
        file_input = await page.querySelector('input[type="file"]')
        await file_input.uploadFile(pdf_path)
        print(f"Uploaded file from '{pdf_path}' successfully.")

    async def fill_inputs(self, page):
        print("Loading input typing...")
        input_elements = await page.querySelectorAll('input.artdeco-text-input--input')
        for input_element in input_elements:
            await input_element.focus()
            await input_element.click({'clickCount': 3})
            await input_element.press('Backspace')
            await input_element.type('5')
        print("Filled all input fields.")

        select_elements = await page.querySelectorAll('select')
        for select_element in select_elements:
            options = await select_element.querySelectorAll('option')
            if options:
                last_option_value = await (await options[-1].getProperty('value')).jsonValue()
                await page.evaluate('(element, value) => element.value = value', select_element, last_option_value)
                await page.evaluate('(element) => element.dispatchEvent(new Event("change"))', select_element)
        print("Selected options.")

    async def next_action(self, page):
        await page.waitForSelector(
            'button.artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view', {'timeout': 10000}
        )
        await page.click('button.artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view')

    async def select_radio_buttons(self, page):
        print("Selecting radio buttons...")
        fieldsets = await page.querySelectorAll('fieldset[data-test-form-builder-radio-button-form-component="true"]')
        print(fieldsets)
        for fieldset in fieldsets:
            first_option = await fieldset.querySelector('input[type="radio"]')
            if first_option:
                await first_option.click()
                print("Selected the first radio option in a fieldset.")

    async def fill_textareas(self, page):
        print("Filling text areas...")
        textareas = await page.querySelectorAll('textarea.fb-multiline-text.artdeco-text-input--input.artdeco-text-input__textarea.artdeco-text-input__textarea--align-top')
        for textarea in textareas:
            await textarea.focus()
            await textarea.click({'clickCount': 3})
            await textarea.press('Backspace')
            await textarea.type('This is a sample answer.')
        print("Filled all text areas.")

    async def select_checkboxes(self, page):
        print("Selecting checkboxes...")
        div_elements = await page.querySelectorAll('div.fb-text-selectable__option.display-flex')
        for div_element in div_elements:
            checkbox = await div_element.querySelector('input.fb-form-element__checkbox')
            if checkbox:
                is_checked = await page.evaluate('(checkbox) => checkbox.checked', checkbox)
                if not is_checked:
                    await checkbox.click()
                    print("Checkbox selected.")
                else:
                    print("Checkbox already selected.")
            else:
                print("Checkbox not found within div element.")
        print("Finished selecting checkboxes.")


    async def apply_to_job(self, job_url, file_id):
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.setViewport({"width": 1920, "height": 1080})
        await self.load_cookies(page)

        pdf_path = f"./cv/{file_id}.pdf"
        if not os.path.exists(pdf_path):
            await browser.close()
            raise FileNotFoundError(f"File not found: {pdf_path}")

        try:
            await page.goto(job_url)
            print("URL Loaded:", job_url)

            try:
                await page.waitForSelector(
                    'button.jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view',
                    {'timeout': 10000}
                )
            except Exception as e:
                await browser.close()
                return Error("This system only allows one application per job. This job has already been applied to.", 500)

            await asyncio.sleep(2)
            await page.click('button.jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view')
            print("Clicked 'Easy Apply' button.")

            await page.waitForSelector('.artdeco-modal__content', {'timeout': 20000})
            print("Modal opened.")


            modal_selector = 'div.artdeco-modal.artdeco-modal--layer-default.jobs-easy-apply-modal'
            while await page.querySelector(modal_selector):

                await self.select_radio_buttons(page)
                await self.fill_inputs(page)
                await self.fill_textareas(page)
                await self.select_checkboxes(page)

                try:
                    await self.upload_csv(page, "label.jobs-document-upload__upload-button.artdeco-button--secondary.artdeco-button--2.mt2", pdf_path)
                    print("CV uploaded successfully.")
                except Exception as e:
                    print("No file upload option or upload failed:", str(e))

                await self.next_action(page)
                await asyncio.sleep(2)

            print("Completed all steps, modal closed.")

            screenshot_uid = str(uuid.uuid4())
            screenshot_path = os.path.join(self.CAPTURE_PATH, f"{screenshot_uid}.png")
            await page.screenshot({'path': screenshot_path})
            print(f"Screenshot saved at: {screenshot_path}")

            return screenshot_uid  # Return only the UID

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise
        finally:
            await browser.close()
            print("Browser closed.")
