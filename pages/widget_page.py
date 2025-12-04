from playwright.sync_api import Page, expect
from urllib.parse import urlparse, parse_qs


class WidgetPage:
    def __init__(self, page: Page):
        self.page = page
        self.url = 'https://dev.3snet.info/eventswidget/'

        # Locators
        self.step1_header = page.get_by_text("Шаг 1")
        self.width_input = page.locator('input[name="width"]')
        self.height_input = page.locator('input[name="height"]')
        # self.theme_inputs не нужен в __init__, так как мы ищем динамически в методе
        self.generate_btn = page.get_by_role('button', name='Сгенерировать превью')
        self.preview_iframe = page.locator('#preview iframe')
        self.code_textarea = page.locator('#code')
        self.copy_btn = page.locator('#code-copy-button')

        # Custom jQuery dropdown locators
        self.event_type_dropdown = page.locator('.checkselect').filter(has_text='Выбрать тематику')
        self.event_type_popup = self.event_type_dropdown.locator('.checkselect-popup')

    def load(self):
        self.page.goto(self.url)

    def select_event_type(self, type_name: str):
        """Работа с кастомным дропдауном"""
        # Открываем дропдаун
        self.event_type_dropdown.click()
        expect(self.event_type_popup).to_be_visible()

        # Выбираем чекбокс
        checkbox = self.event_type_popup.locator('label').filter(has_text=type_name)
        checkbox.click()

        # Закрываем дропдаун кликом вовне (по заголовку)
        self.step1_header.click()
        expect(self.event_type_popup).to_be_hidden()

    def set_size(self, width: str, height: str):
        """Ввод размеров с эмуляцией Tab для триггера событий blur/change"""
        self.width_input.fill(width)
        self.width_input.press("Tab")

        self.height_input.fill(height)
        self.height_input.press("Tab")

    def select_theme(self, theme_value: str):
        """theme_value: 'blue', 'green', 'turquoise', 'purple'"""
        # Самое надежное: кликаем по родительскому <label>, который является видимой областью для клика.
        # Ищем родителя (label) для скрытого input с нужным value.
        theme_locator = self.page.locator(f'input[name="theme"][value="{theme_value}"]').locator('xpath=..')
        theme_locator.click()

    def generate_preview(self):
        self.generate_btn.click()
        expect(self.preview_iframe).to_be_visible()

    def get_iframe_src_params(self) -> dict:
        """Парсим URL внутри iframe для проверок"""
        src = self.preview_iframe.get_attribute('src')
        if not src:
            raise ValueError("Iframe src is empty")

        parsed = urlparse(src)
        return parse_qs(parsed.query)

    def get_generated_code(self) -> str:
        return self.code_textarea.input_value()