from openwiden import views, exceptions

from rest_framework import status


class TestExceptionHandler:
    def test_service_exception(self):
        exception = exceptions.ServiceException("description")
        response = views.exception_handler(exception=exception, context=None)

        assert response.data == exception.description
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_drf_handler(self):
        response = views.exception_handler(exception=ValueError, context=None)

        assert response is None
