from instagram_app.tests.shared_helpers import get_fixtures_path
import setup_django
setup_django.setup_tests()

from instagram_app.models import Profile
from instagram_app.serializers import ProfileSerializer
from django.urls import reverse
from shared_helpers import create_test_user
from django.core.files.uploadedfile import SimpleUploadedFile

from views.view_test_base import ViewTestBase


class TestProfilesViewSet(ViewTestBase):
    def setUp(self):
        super().setUp()
    def test_retrieve(self):
        test_profile = create_test_user().profile
        url = reverse("profiles-detail", kwargs={
            'pk': test_profile.pk
        })
        expected_response = ProfileSerializer(instance=test_profile).data
        self.request_test(url, self.client.get, {}, expected_response, 200)
    def test_profiles_me(self): 
        me = self.sign_in_random_user() 
        url = reverse("profiles-me") 
        expected_response = ProfileSerializer(instance=me.profile).data 
        self.request_test(url, self.client.get, {}, expected_response, 200) 
    def test_profiles_me_not_logged_in(self): 
        url = reverse("profiles-me") 
        expected_response = {
            'detail': 'Authentication credentials were not provided.'
        } 
        self.request_test(url, self.client.get, {}, expected_response, 401) 
    
    def test_profiles_retrieve_follows(self): 
        test_user = create_test_user().profile

        user1 = create_test_user().profile
        user2 = create_test_user().profile
        user1.followers.add(test_user) 
        user2.followers.add(test_user)

        url = reverse("profiles-follows", kwargs={
            'pk': test_user.pk
        }) 

        expected_response = {
            'users': [user.pk for user in test_user.follows.all()]
        }
        self.request_test(url, self.client.get, {}, expected_response, 200)
    def test_toggle_follow_for_following(self): 
        test_user = self.sign_in_random_user().profile 
        user = create_test_user().profile 
        url = reverse("profiles-toggle-follow", kwargs={
            'pk': user.pk
        })
        self.request_test(url, self.client.post, {}, {}, 200) 
        # verify the user was really followed 
        self.assertEqual(
            list(user.followers.all()), 
            [test_user]
        )
    def test_toggle_follow_to_unfollow(self): 
        test_user = self.sign_in_random_user().profile 
        user = create_test_user().profile 
        user.followers.add(test_user) 
        url = reverse("profiles-toggle-follow", kwargs={
            'pk': user.pk
        })
        self.request_test(url, self.client.post, {}, {}, 200) 
        # verify that the user is now not followed 
        self.assertEqual(
            list(Profile(pk=user.pk).followers.all()), 
            []
        )

    def test_retrieve_404(self):
        url = reverse("profiles-detail", kwargs={
            'pk': 424242
        })
        expected_response = {
            'detail': 'Not found.'
        }
        self.request_test(url, self.client.get, {}, expected_response, 404)
    def test_update_about(self):
        user = self.sign_in_random_user()
        url = reverse("profiles-detail", kwargs={
            'pk': user.profile.pk,
        })
        data = {
            "about": "Updated about"
        }
        self.request_test(url, self.client.put, data, {}, 200)
        # validate that profile has been updated
        self.assertEqual(
            Profile.objects.get(pk=user.profile.pk).about,
            data['about']
        )
    def test_update_404(self):
        self.sign_in_random_user()
        url = reverse("profiles-detail", kwargs={
            'pk': 424242
        })
        data = {
            'about': "updated about"
        }
        expected_response = {
            'detail': 'Not found.'
        }
        self.request_test(url, self.client.put, data, expected_response, 404)
    def test_update_from_another_user(self):
        author = create_test_user()
        another_user = self.sign_in_random_user()
        url = reverse("profiles-detail", kwargs={
            'pk': author.profile.pk
        })
        data = {
            "about": "updated about"
        }
        expected_response = {}
        self.request_test(url, self.client.put, data, expected_response, 403)
        # validate that profile has NOT been updated 
        self.assertEqual(
            Profile.objects.get(pk=author.profile.pk).about, 
            author.profile.about
        )
    
    def test_avatar_update(self): 
        user = self.sign_in_random_user() 
        url = reverse("profiles-avatar") 
        with open(get_fixtures_path() + "test_avatar.png", 'rb') as f: 
            avatar_file = f.read()
        data = {
            'file': SimpleUploadedFile("test_avatar.png", avatar_file, content_type="image/png")
        }  
        self.request_test(url, lambda **kwargs: self.client.post(format="multipart", **kwargs), data, {}, 200) 
        #verify avatar was updated 
        self.assertNotEqual(
            Profile.objects.get(pk=user.profile.pk).avatar, 
            None
        )
    def test_avatar_update_403(self): 
        url = reverse("profiles-avatar") 
        data = {
            'file': 'dummy'
        }
        expected_response = {
            "detail": "Authentication credentials were not provided."
        }
        self.request_test(
            url, 
            lambda **kwargs: self.client.post(format="multipart", **kwargs), 
            data, 
            expected_response, 
            401
        )
    def test_avatar_update_not_image(self): 
        user = self.sign_in_random_user() 
        url = reverse("profiles-avatar") 

        with open(get_fixtures_path() + "test_injection.js", 'rb') as f: 
            injection_file = f.read() 
        name = "test_avatar.png" # this is on purpose a .png
        content_type = "image/png" # this is on purpose an image
        data = {
            'file': SimpleUploadedFile(name, injection_file, content_type=content_type)
        }
        expected_response = {
            "detail": "What you uploaded is not a valid image."
        }
        self.request_test(url, lambda **kwargs: self.client.post(format="multipart", **kwargs), data, expected_response, 400) 
        print(Profile.objects.get(pk=user.profile.pk).avatar)
        