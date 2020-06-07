import json
import os
import pytest
import typing as t

from enum import Enum, auto

from django.urls import reverse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

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


def oauth_redirect(driver: webdriver.Remote) -> t.Union[bool, OAuthRedirectType]:
    """
    Custom redirect waiter for selenium driver.
    """
    if driver.current_url == "https://github.com/sessions/verified-device":
        return OAuthRedirectType.VERIFY_DEVICE
    elif driver.current_url.startswith("https://github.com/login/oauth/authorize"):
        return OAuthRedirectType.AUTHORIZE
    elif driver.current_url.startswith("http://0.0.0.0:5000/"):
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
    selenium.save_screenshot("./selenium/verify_set_code.png")

    # Click on verify button
    verify_button.click()
    selenium.save_screenshot("./selenium/verify_clicked.png")


def authorize(selenium: webdriver.Remote) -> None:
    try:
        authorize_button = selenium.find_element_by_xpath("//button[@name='authorize']")
    except NoSuchElementException:
        # Do nothing (already completed case)
        return

    # Select & submit clicks + 1 for just in case
    for _ in range(3):
        authorize_button.click()
    selenium.save_screenshot("./selenium/authorize_clicked.png")

    # Additional wait
    selenium.implicitly_wait(3)
    selenium.save_screenshot("./selenium/authorize_success.png")


def test_run(selenium, live_server, create_api_client):
    url = live_server.url + reverse("api-v1:auth:login", kwargs={"vcs": VersionControlService.GITHUB.value})
    wait = WebDriverWait(selenium, 10)

    # Open API url, that redirects to sign in form
    selenium.get(url)

    # Sign in
    selenium.save_screenshot("./selenium/sign_in_open.png")
    selenium.find_element_by_id("login_field").send_keys(GITHUB_USER_LOGIN)
    selenium.find_element_by_id("password").send_keys(GITHUB_USER_PASSWORD)
    selenium.find_element_by_xpath("//input[@name='commit' and @value='Sign in']").click()
    selenium.save_screenshot("./selenium/sign_in_clicked.png")

    # Wait for redirect and check received type
    try:
        redirect_type = wait.until(oauth_redirect, "url: {url}".format(url=selenium.current_url))
    finally:
        # Save page for debugging on fail
        path = os.path.join(os.path.dirname(__file__), "selenium/sign_in_clicked.html")
        with open(path, "w") as file:
            file.write(selenium.current_url)
            file.write(selenium.page_source)

    # Do action depends on redirect type
    if redirect_type == OAuthRedirectType.AUTHORIZE:
        authorize(selenium)
    elif redirect_type == OAuthRedirectType.VERIFY_DEVICE:
        verify_device(selenium)

    # OAuth complete
    url = selenium.current_url.replace("http://0.0.0.0:5000", live_server.url)
    complete_url = "view-source:{url}&format=json".format(url=url)
    selenium.get(complete_url)
    selenium.save_screenshot("./selenium/complete.png")

    pre_element = selenium.find_element_by_tag_name("pre")
    tokens = json.loads(pre_element.text)

    # Get user
    client = create_api_client(access_token=tokens["access"])
    response = client.get(reverse("api-v1:user-me"))

    assert response.status_code == 200
    assert response.data["username"] == GITHUB_USER_LOGIN
