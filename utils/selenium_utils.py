from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def hide_element(driver: WebDriver, element: WebElement) -> None:
    driver.execute_script('arguments[0].style.visibility="hidden";', element)


def show_element(driver: WebDriver, element: WebElement) -> None:
    driver.execute_script('arguments[0].style.visibility="visible";', element)
