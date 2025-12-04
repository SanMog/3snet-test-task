import pytest
from playwright.sync_api import expect, Page


def test_generate_custom_widget(widget_page):
    """
    E2E тест генерации виджета с кастомными настройками.
    Проверяет: ввод данных, генерацию превью, соответствие кода и iframe.
    """
    # 1. Arrange (Подготовка)
    widget_page.load()

    target_width = "500"
    target_height = "600"
    target_theme = "purple"
    target_category = "Blockchain"
    target_category_id = "10963"  # ID из HTML для Blockchain

    # 2. Act (Действия)
    widget_page.select_event_type(target_category)
    widget_page.set_size(target_width, target_height)
    widget_page.select_theme(target_theme)
    widget_page.generate_preview()

    # 3. Assert (Проверки)

    # A. Проверка параметров внутри src атрибута iframe
    params = widget_page.get_iframe_src_params()
    assert params.get('theme')[0] == target_theme, "Тема в URL iframe не совпадает"
    assert target_category_id in params.get('event_type')[0], "ID категории не найден в URL"

    # B. Проверка физических атрибутов iframe
    expect(widget_page.preview_iframe).to_have_attribute("width", target_width)
    expect(widget_page.preview_iframe).to_have_attribute("height", target_height)

    # C. Проверка сгенерированного HTML кода
    code = widget_page.get_generated_code()
    assert f'width="{target_width}"' in code
    assert f'height="{target_height}"' in code
    assert f'theme={target_theme}' in code


def test_copy_code_to_clipboard(page: Page, widget_page):
    """
    Проверка функционала кнопки копирования в буфер обмена.
    Требует выдачи прав браузеру.
    """
    # Выдаем права на чтение/запись буфера
    context = page.context
    context.grant_permissions(["clipboard-read", "clipboard-write"])

    widget_page.load()
    widget_page.generate_preview()

    # Клик по кнопке копирования
    widget_page.copy_btn.click()

    # Проверка UX: текст кнопки изменился
    expect(widget_page.copy_btn).to_have_text("Скопировано")

    # Проверка содержимого буфера
    clipboard_text = page.evaluate("navigator.clipboard.readText()")
    textarea_text = widget_page.get_generated_code()

    assert clipboard_text == textarea_text, "Текст в буфере не совпадает с кодом в поле"


def test_size_input_validation(widget_page):
    """
    Boundary testing: Проверка авто-коррекции ввода.
    Сайт не позволяет ввести ширину меньше 230px.
    """
    widget_page.load()

    # Пытаемся ввести 100px (меньше минимума)
    widget_page.set_size("100", "240")
    widget_page.generate_preview()

    # Ожидаем, что поле сбросилось на минимальное значение (230)
    expect(widget_page.width_input).to_have_value("230")