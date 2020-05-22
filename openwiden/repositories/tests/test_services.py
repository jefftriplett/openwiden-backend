from unittest import mock

import pytest
from django.utils.timezone import now

from openwiden import enums, exceptions, services as remote_services
from openwiden.repositories import services, models, error_messages


class TestRepositoryService:
    @mock.patch.object(models.Repository.objects, "create")
    @mock.patch.object(models.Repository.objects, "get")
    def test_sync(self, patched_get, patched_create, mock_repo):
        expected_repo = mock_repo
        patched_get.return_value = expected_repo

        repo = services.Repository.sync("", 1, "", "", now(), now())

        assert repo == (expected_repo, False)

        patched_get.side_effect = models.Repository.DoesNotExist
        patched_create.return_value = expected_repo

        repo = services.Repository.sync("", 1, "", "", now(), now())

        assert repo == (expected_repo, True)

        assert patched_get.call_count == 2
        assert patched_create.call_count == 1

    @mock.patch.object(remote_services, "get_service")
    @mock.patch.object(services.repository, "async_task")
    @mock.patch.object(services.repository.users_services.VCSAccount, "find")
    def test_add(self, p_find, p_task, p_get_service, mock_repo, mock_vcs_account, mock_remote_service, mock_user):
        expected_task_id = "12345"
        repo = mock_repo
        repo.vcs = "test"
        repo.is_added = False
        repo.visibility = enums.VisibilityLevel.public
        p_find.return_value = mock_vcs_account
        p_get_service.return_value = mock_remote_service
        p_task.return_value = expected_task_id

        task_id = services.Repository.add(repo, mock_user)

        assert task_id == expected_task_id

        with pytest.raises(exceptions.ServiceException) as e:
            repo.is_added = True
            services.Repository.add(repo, mock_user)
            assert e.value == error_messages.REPOSITORY_ALREADY_ADDED

        with pytest.raises(exceptions.ServiceException) as e:
            repo.is_added = False
            repo.visibility = enums.VisibilityLevel.private
            services.Repository.add(repo, mock_user)
            assert e.value == error_messages.REPOSITORY_IS_PRIVATE_AND_CANNOT_BE_ADDED

        assert p_find.call_count == 3
        assert p_get_service.call_count == 1
        assert p_task.call_count == 1

    @pytest.mark.django_db
    def test_get_user_repos(self, create_repository, user, org, create_member, create_vcs_account):
        user_repos = [
            create_repository(owner__user=user, organization=None),
            create_repository(owner=None, organization=org),
        ]
        create_repository(owner=None, organization=None)
        create_member(organization=org, vcs_account=create_vcs_account(user=user))

        qs = services.Repository.get_user_repos(user)

        assert qs.count() == len(user_repos)
        assert models.Repository.objects.count() == len(user_repos) + 1


class TestIssueService:
    @mock.patch.object(models.Issue.objects, "update_or_create")
    def test_sync(self, patched_update_or_create, mock_issue, mock_repo):
        patched_update_or_create.return_value = mock_issue, True

        assert services.Issue.sync(
            repo=mock_repo,
            remote_id=1,
            title="title",
            description=None,
            state="open",
            labels=["label"],
            url="http://example.com",
            created_at=now(),
            updated_at=now(),
        ) == (mock_issue, True)
