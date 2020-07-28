from openwiden import exceptions


def test_service_exception():
    assert str(exceptions.ServiceException("description")) == "description"
