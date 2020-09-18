from openwiden import views


class TestExceptionHandler:
    def test_drf_handler(self):
        response = views.exception_handler(exception=ValueError, context=None)

        assert response is None
