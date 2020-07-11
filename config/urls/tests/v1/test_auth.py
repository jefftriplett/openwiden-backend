from django.urls import resolve, reverse

from openwiden import enums


def test_login():
    vcs = enums.VersionControlService.GITHUB
    url = f"/api/v1/auth/login/{vcs}/"
    namespace = "api-v1:login"

    assert reverse(namespace, kwargs={"vcs": vcs}) == url
    assert resolve(url).view_name == namespace


def test_complete():
    vcs = enums.VersionControlService.GITLAB
    url = f"/api/v1/auth/complete/{vcs}/"
    namespace = "api-v1:complete"

    assert reverse(namespace, kwargs={"vcs": vcs}) == url
    assert resolve(url).view_name == namespace


def test_refresh():
    url = "/api/v1/auth/refresh_token/"
    namespace = "api-v1:refresh_token"

    assert reverse(namespace) == url
    assert resolve(url).view_name == namespace
