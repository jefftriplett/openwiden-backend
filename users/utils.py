from .models import User, OAuth2Token


def create_or_update_user(provider: str, client, token):
    user = None

    if provider == "github":
        profile = client.get("user", token=token).json()
        remote_id = profile["id"]
        login = profile["login"]
        email = profile["email"]
        first_name, sep, last_name = profile["name"].partition(" ")

        try:
            oauth2_token = OAuth2Token.objects.get(provider=provider, remote_id=remote_id)

            if oauth2_token.login != login:
                oauth2_token.login = login
                oauth2_token.save()

            user = oauth2_token.user

        except OAuth2Token.DoesNotExist:
            user, created = User.objects.get_or_create(username=login)

            if created:
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            OAuth2Token.objects.create(
                user=user,
                provider=provider,
                remote_id=remote_id,
                login=login,
                access_token=token["access_token"],
                token_type=token["token_type"],
            )

    return user
