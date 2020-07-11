from django.urls import reverse, resolve


class TestRepositoriesUrls:
    def test_list(self):
        url = "/api/v1/repositories/"
        namespace = "api-v1:repo-list"

        assert reverse(namespace) == url
        assert resolve(url).view_name == namespace

    def test_detail(self):
        url = "/api/v1/repositories/1/"
        namespace = "api-v1:repo-detail"

        assert reverse(namespace, kwargs={"id": 1}) == url
        assert resolve(url).view_name == namespace


class TestIssuesUrls:
    def test_list(self):
        url = "/api/v1/repositories/1/issues/"
        namespace = "api-v1:repo-issue-list"

        assert reverse(namespace, kwargs={"repository_id": 1}) == url
        assert resolve(url).view_name == namespace

    def test_detail(self):
        url = "/api/v1/repositories/1/issues/1/"
        namespace = "api-v1:repo-issue-detail"

        assert reverse(namespace, kwargs={"repository_id": 1, "id": 1}) == url
        assert resolve(url).view_name == namespace


class TestUserRepositoriesUrls:
    def test_list(self):
        url = "/api/v1/user/repositories/"
        namespace = "api-v1:user-repo-list"

        assert reverse(namespace) == url
        assert resolve(url).view_name == namespace

    def test_detail(self):
        url = "/api/v1/user/repositories/1/"
        namespace = "api-v1:user-repo-detail"

        assert reverse(namespace, kwargs={"id": 1}) == url
        assert resolve(url).view_name == namespace

    def test_add(self):
        url = "/api/v1/user/repositories/1/add/"
        namespace = "api-v1:user-repo-add"

        assert reverse(namespace, kwargs={"id": 1}) == url
        assert resolve(url).view_name == namespace
