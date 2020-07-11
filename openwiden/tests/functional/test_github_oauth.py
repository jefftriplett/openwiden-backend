import json
import os
import pytest
import typing as t

from enum import Enum, auto

from django.urls import reverse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from openwiden.enums import VersionControlService

from .utils import search_github_verification_code

pytestmark = [pytest.mark.django_db, pytest.mark.functional]


GITHUB_USER_LOGIN = os.getenv("TEST_GITHUB_USER_LOGIN")
GITHUB_USER_PASSWORD = os.getenv("TEST_GITHUB_USER_PASSWORD")

EMAIL_LOGIN = os.getenv("TEST_EMAIL_LOGIN")
EMAIL_PASSWORD = os.getenv("TEST_EMAIL_PASSWORD")
EMAIL_IMAP_HOST = os.getenv("TEST_EMAIL_IMAP_HOST")


class OAuthRedirectType(Enum):
    VERIFY_DEVICE = auto()
    AUTHORIZE = auto()
    COMPLETE = auto()


def save_current_state(driver: webdriver.Remote, name: str):
    """
    Selenium debug helper.
    """
    driver.step = getattr(driver, "step", 1)

    # Build path
    path = os.path.join(os.path.dirname(__file__), "selenium")
    page_src_path = os.path.join(path, "{step}_{name}.html".format(step=driver.step, name=name))
    screenshot_path = os.path.join(path, "{step}_{name}.png".format(step=driver.step, name=name))

    # Save page source
    with open(page_src_path, "w") as file:
        file.write(driver.current_url)
        file.write(driver.page_source)

    # Save browser screenshot
    driver.save_screenshot(screenshot_path)

    driver.step += 1


def oauth_redirect(driver: webdriver.Remote) -> t.Union[bool, OAuthRedirectType]:
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


def verify_device(selenium: webdriver.Remote) -> None:
    verify_button = selenium.find_element_by_xpath("//button[contains(text(), 'Verify')]")

    # Get verification code from email
    verification_code = search_github_verification_code(
        user=EMAIL_LOGIN,
        password=EMAIL_PASSWORD,
        imap_host=EMAIL_IMAP_HOST,
    )

    # Set code
    selenium.find_element_by_id("otp").send_keys(verification_code)
    save_current_state(selenium, "verify_set_code")

    # Click on verify button
    verify_button.click()
    save_current_state(selenium, "verify_clicked")


def authorize(selenium: webdriver.Remote) -> None:
    try:
        authorize_button = selenium.find_element_by_xpath("//button[@name='authorize']")
    except NoSuchElementException:
        # Do nothing (already completed case)
        return

    # Select & submit clicks + 1 for just in case
    wait = WebDriverWait(selenium, 10)
    wait.until(expected_conditions.staleness_of(authorize_button))
    authorize_button.click()
    save_current_state(selenium, "authorize_clicked")

    selenium.implicitly_wait(3)
    save_current_state(selenium, "authorize_success")


def test_run(selenium, live_server, create_api_client):
    url = live_server.url + reverse("api-v1:login", kwargs={"vcs": VersionControlService.GITHUB.value})
    wait = WebDriverWait(selenium, 10)

    # Open API url, that redirects to sign in form
    selenium.get(url)

    # Sign in
    save_current_state(selenium, "sign_in_open")
    selenium.find_element_by_id("login_field").send_keys(GITHUB_USER_LOGIN)
    selenium.find_element_by_id("password").send_keys(GITHUB_USER_PASSWORD)
    selenium.find_element_by_xpath("//input[@name='commit' and @value='Sign in']").click()
    save_current_state(selenium, "sign_in_clicked")

    # Wait for redirect and check received type
    try:
        redirect_type = wait.until(oauth_redirect, "url: {url}".format(url=selenium.current_url))
    finally:
        save_current_state(selenium, "sign_in_redirect_fail")

    # Do action depends on redirect type
    if redirect_type == OAuthRedirectType.AUTHORIZE:
        authorize(selenium)
    elif redirect_type == OAuthRedirectType.VERIFY_DEVICE:
        verify_device(selenium)

    save_current_state(selenium, "after_redirect")

    # Check if authorize is required
    try:
        redirect_type = wait.until(oauth_redirect, "url: {url}".format(url=selenium.current_url))
    finally:
        save_current_state(selenium, "sign_in_redirect_fail")

    # Check if authorize required
    if redirect_type == OAuthRedirectType.AUTHORIZE:
        authorize(selenium)
    elif redirect_type != OAuthRedirectType.COMPLETE:
        raise ValueError(redirect_type)

    # OAuth complete
    url = selenium.current_url.replace("http://0.0.0.0:8000", live_server.url)
    print(url)
    complete_url = "view-source:{url}&format=json".format(url=url)
    selenium.get(complete_url)
    # wait.until(lambda driver: driver.current_url.startswith("https://github.com/login/oauth/authorize") is False)
    save_current_state(selenium, "complete")

    pre_element = selenium.find_element_by_tag_name("pre")
    tokens = json.loads(pre_element.text)

    # Get user
    client = create_api_client(access_token=tokens["access"])
    response = client.get(reverse("api-v1:user-me"))

    assert response.status_code == 200
    assert response.data["username"] == GITHUB_USER_LOGIN
