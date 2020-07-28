import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

SIGN_IN_BUTTON_XPATH = "//input[@name='commit' and @value='Sign in']"
DRIVER_PATH = "/Users/stefanitsky/Downloads/chromedriver"

# Gitlab account credentials
USER_LOGIN = os.getenv("TEST_GITLAB_USER_LOGIN")
USER_PASSWORD = os.getenv("TEST_GITLAB_USER_PASSWORD")

# Init driver and waiter
driver = webdriver.Chrome(DRIVER_PATH)
wait = WebDriverWait(driver, 10)


def sign_in_page_is_loaded(driver: webdriver.Remote) -> bool:
    try:
        driver.find_element_by_xpath(SIGN_IN_BUTTON_XPATH)
    except NoSuchElementException:
        return False
    else:
        return True


# Open API url, that redirect to Gitlab sign in
driver.get(
    "http://0.0.0.0:8000" "/api/v1/auth/login/gitlab/" "?redirect_uri=http://0.0.0.0:8000/api/v1/auth/complete/gitlab/"
)

# Checking your Browser - GitLab
wait.until(lambda d: d.title != "Checking your Browser - GitLab")

# Sign in
wait.until(sign_in_page_is_loaded)

# Insert user credentials and try to sign in
driver.find_element_by_id("user_login").send_keys(USER_LOGIN)
driver.find_element_by_id("user_password").send_keys(USER_PASSWORD)
driver.find_element_by_xpath(SIGN_IN_BUTTON_XPATH).click()

wait.until(lambda d: d.title == "User Settings · GitLab")

# Authorize
driver.find_element_by_xpath("//input[@name='commit' and @value='Authorize']").click()
wait.until(lambda d: d.title != "User Settings · GitLab")
