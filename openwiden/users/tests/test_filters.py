# from django.test import SimpleTestCase
#
# from openwiden.users.filters import OAuthCompleteFilter
#
#
# class Test(SimpleTestCase):
#     def test_oauth_complete_filter_get_schema_operation_parameters(self):
#         parameters = OAuthCompleteFilter().get_schema_operation_parameters(None)
#         expected = [
#             {
#                 "name": "code",
#                 "in": "query",
#                 "required": True,
#                 "description": "Received code for token exchange.",
#                 "schema": {"type": "string",},
#             },
#             {
#                 "name": "state",
#                 "in": "query",
#                 "required": True,
#                 "description": (
#                     "An unguessable random string. It is used to protect against cross-site request forgery attacks."
#                 ),
#                 "schema": {"type": "string",},
#             },
#         ]
#         self.assertEqual(parameters, expected)
