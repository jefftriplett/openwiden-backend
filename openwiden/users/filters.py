from rest_framework.filters import BaseFilterBackend


class OAuthCompleteFilter(BaseFilterBackend):
    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "code",
                "in": "query",
                "required": True,
                "description": "Received code for token exchange.",
                "schema": {"type": "string",},
            },
            {
                "name": "state",
                "in": "query",
                "required": True,
                "description": (
                    "An unguessable random string. It is used to protect against cross-site request forgery attacks."
                ),
                "schema": {"type": "string",},
            },
        ]
