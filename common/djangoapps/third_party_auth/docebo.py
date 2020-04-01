from social_core.backends.oauth import BaseOAuth2


class DoceboOAuth2(BaseOAuth2):
    """Docebo OAuth authentication backend"""
    name = 'docebo'
    ACCESS_TOKEN_METHOD = 'POST'
    ID_KEY = "id"

    def api_path(self, path=''):
        """Build API path for Docebo domain"""
        return 'https://{domain}/{path}'.format(domain=self.setting('DOMAIN'), path=path)

    def authorization_url(self):
        return self.api_path('oauth2/authorize')

    def access_token_url(self):
        return self.api_path('oauth2/token')

    def user_data(self, access_token, *args, **kwargs):
        data = self.get_json(
            self.api_path('manage/v1/user/session'),
            headers={
                'Authorization': 'Bearer {}'.format(access_token)
            }
        ).get('data')
        return data

    def get_user_details(self, response):
        """Return user details from amazon account"""
        first_name = response.get('firstname')
        last_name = response.get('lastname')
        return {
            'username': response.get('username'),
            'email': response.get('email'),
            'name': "{} {}".format(first_name, last_name),
            'first_name': first_name,
            'last_name': last_name,
            'user_id': response.get('id'),
            'picture': response.get('avatar_url'),
        }
