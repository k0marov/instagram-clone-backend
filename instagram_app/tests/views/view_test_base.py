from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
import uuid
import json 

class ViewTestBase(TestCase): 
    def setUp(self): 
        self.client = APIClient() 

    def sign_in_random_user(self): 
        new_user = get_user_model()(
            username=str(uuid.uuid4()), 
        )
        new_user.set_password("321")
        new_user.save()
        self.client.login(username=new_user.username, password="321")
        return new_user
    def request_test(self, path, method, data, expected_response, status_code): 
        # method is the self.client.get, self.client.post, etc
        # act 
        response = method(
            path=path, 
            data=data, 
            HTTP_ACCEPT="application/json"
        )
        # assert 
        response_content = json.loads(response.content) if response.content else {} 
        if expected_response != None: 
            self.assertEqual(
                response_content, 
                expected_response
            )
        self.assertEqual(
            response.status_code, 
            status_code
        )

        return response_content