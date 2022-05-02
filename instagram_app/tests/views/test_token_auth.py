from ssl import create_default_context
import setup_django
setup_django.setup_tests()

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token 

from views.view_test_base import ViewTestBase


class TestTokenAuth(ViewTestBase): 
    test_username = "user1"
    test_password = "12345"
    def test_login(self): 
        user = get_user_model()(
            username=self.test_username,
        )
        user.set_password(self.test_password)
        user.save()
        url = reverse('api-token-login')
        data = {
            'username': self.test_username,
            'password': self.test_password,
        }
        expected_response = {
            'token': str(Token.objects.get(user=user))
        }
        self.request_test(url, self.client.post, data, expected_response, 200)
    def test_login_wrong_data(self): 
        url = reverse('api-token-login') 
        data = {
            'username': 'only-username'
        }
        self.request_test(url, self.client.post, data, None, 400)
    def test_registration(self): 
        data = {
            'username': self.test_username, 
            'password': self.test_password, 
        }
        url = reverse("api-token-register") 
        response = self.request_test(url, self.client.post, data, None, 200)
        token = Token.objects.get(key=response['token'])
        created_user = token.user
        self.assertEqual(
            created_user.username, 
            self.test_username,
        )
        self.assertTrue(
            check_password(self.test_password, created_user.password)
        )
    def test_registration_wrong_data(self): 
        data = {
            'username': 'user-without-password'
        }
        url = reverse("api-token-register") 
        self.request_test(url, self.client.post, data, {}, 400)

