import os
import typing as t
import imaplib
import time

from enum import Enum, auto

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

GITHUB_VERIFICATION_CODE_LENGTH = 6

GITHUB_USER_LOGIN = os.getenv("TEST_GITHUB_USER_LOGIN")
GITHUB_USER_PASSWORD = os.getenv("TEST_GITHUB_USER_PASSWORD")

EMAIL_LOGIN = os.getenv("TEST_EMAIL_LOGIN")
EMAIL_PASSWORD = os.getenv("TEST_EMAIL_PASSWORD")
EMAIL_IMAP_HOST = os.getenv("TEST_EMAIL_IMAP_HOST")


def search_github_verification_code(user: str, password: str, imap_host: str, timeout: int = 60) -> str:
    """
    Connects to the imap server and returns verification code.
    """
    connection = imaplib.IMAP4_SSL(imap_host)
    connection.login(user=user, password=password)

    while True:
        connection.select(mailbox="INBOX")
        typ, data = connection.search(None, '(SUBJECT "[GitHub] Please verify your device")')

        if typ == "OK":
            messages_ids = data[0].split()

            # Check for a new messages
            if len(messages_ids) == 0:
                if timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                    continue
                else:
                    raise Exception("e-mail search failed (timed out).")

            # Fetch last e-mail
            typ, data = connection.fetch(messages_ids[-1], "(RFC822)")

            if typ == "OK":
                email_text = data[0][1]

                # Parse email for code
                search_text = "Verification code: "
                start = email_text.find(search_text.encode()) + len(search_text)
                end = start + GITHUB_VERIFICATION_CODE_LENGTH
                code = email_text[start:end]

                # Delete all messages before connection close
                for message_id in messages_ids:
                    connection.store(message_id, "+FLAGS", "\\Deleted")
                connection.expunge()

                # Close connection and logout
                connection.close()
                connection.logout()

                # Return code
                return code.decode()
            else:
                raise Exception("Fetch failed")


class OAuthRedirectType(Enum):
    VERIFY_DEVICE = auto()
    AUTHORIZE = auto()
    COMPLETE = auto()


def oauth_redirect(driver) -> t.Union[bool, OAuthRedirectType]:
    """
    Custom redirect waiter for selenium driver.
    """
    if driver.current_url == "https://github.com/sessions/verified-device":
        return OAuthRedirectType.VERIFY_DEVICE
    elif driver.current_url.startswith("https://github.com/login/oauth/authorize"):
        return OAuthRedirectType.AUTHORIZE
    elif driver.current_url.startswith("http://0.0.0.0:8000/"):
        return OAuthRedirectType.COMPLETE
    else:
        return False


def code_confirm_page_is_loaded() -> bool:
    try:
        return driver.find_element_by_xpath("//button[contains(text(), 'Verify')]")
    except NoSuchElementException:
        return False


def verify_device(driver) -> None:
    verify_button = None

    try:
        verify_button = wait.until(code_confirm_page_is_loaded)
    except TimeoutException:
        pass

    # Get verification code from email
    verification_code = search_github_verification_code(
        user=EMAIL_LOGIN, password=EMAIL_PASSWORD, imap_host=EMAIL_IMAP_HOST,
    )

    # Set code
    driver.find_element_by_id("otp").send_keys(verification_code)

    # Click on verify button
    verify_button.click()


def authorize(driver) -> None:
    try:
        authorize_button = driver.find_element_by_xpath("//button[@name='authorize']")
    except NoSuchElementException:
        # Do nothing (already completed case)
        return

    # Select & submit clicks + 1 for just in case
    wait.until(expected_conditions.staleness_of(authorize_button))
    authorize_button.click()

    driver.implicitly_wait(3)


DRIVER_PATH = "/Users/stefanitsky/Downloads/chromedriver"
driver = webdriver.Chrome(DRIVER_PATH)
url = "http://0.0.0.0:8000/api/v1/auth/login/github/"
wait = WebDriverWait(driver, 10)

# Open API url, that redirects to sign in form
driver.get(url)

# Sign in
driver.find_element_by_id("login_field").send_keys(GITHUB_USER_LOGIN)
driver.find_element_by_id("password").send_keys(GITHUB_USER_PASSWORD)
driver.find_element_by_xpath("//input[@name='commit' and @value='Sign in']").click()

# Wait for redirect and check received type
redirect_type = None
try:
    redirect_type = wait.until(oauth_redirect, "url: {url}".format(url=driver.current_url))
except TimeoutException:
    pass

# Do action depends on redirect type
if redirect_type == OAuthRedirectType.AUTHORIZE:
    authorize(driver)
elif redirect_type == OAuthRedirectType.VERIFY_DEVICE:
    verify_device(driver)

# Check if authorize is required
try:
    redirect_type = wait.until(oauth_redirect, "url: {url}".format(url=driver.current_url))
except TimeoutException:
    pass

# Check if authorize required
if redirect_type == OAuthRedirectType.AUTHORIZE:
    authorize(driver)
elif redirect_type != OAuthRedirectType.COMPLETE:
    raise ValueError(redirect_type)
