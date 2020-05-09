from openwiden.users import permissions


def test_is_user_or_admin_or_readonly(api_rf, mock_view, mock_user):
    permission = permissions.IsUserOrAdminOrReadOnly()
    request = api_rf.get("/fake-url/")

    assert permission.has_object_permission(request, mock_view, mock_user) is True

    request = api_rf.post("/fake-url/")
    request.user = mock_user
    admin_user = mock_user
    admin_user.is_superuser = True

    assert permission.has_object_permission(request, mock_view, admin_user) is True

    request.user = mock_user
    request.user.is_superuser = False

    assert permission.has_object_permission(request, mock_view, mock_user) is True
