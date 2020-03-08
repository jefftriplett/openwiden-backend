from .models import User, OAuth2Token


def get_or_create_user(provider: str, client, token):
    user = None

    if provider == "github":
        profile = client.get("user", token=token).json()
        remote_id = profile["id"]
        login = profile["login"]
        email = profile["email"]
        first_name, last_name = profile["name"].split(" ")

        try:
            oauth2_token = OAuth2Token.objects.get(provider=provider, remote_id=remote_id)

            if oauth2_token.login != login:
                oauth2_token.login = login
                oauth2_token.save()

            user = oauth2_token.user

        except OAuth2Token.DoesNotExist:
            user = User.objects.create(username=login, first_name=first_name, last_name=last_name, email=email)
            OAuth2Token.objects.create(user=user, provider=provider, remote_id=remote_id, login=login, **token)

    return user
