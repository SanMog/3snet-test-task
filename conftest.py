import pytest
from pages.widget_page import WidgetPage

@pytest.fixture
def widget_page(page):
    """Фикстура, предоставляющая объект страницы виджета"""
    return WidgetPage(page)