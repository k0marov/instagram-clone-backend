import setup_django
setup_django.setup_tests()

from instagram_app.models import Post, Comment
from instagram_app.serializers import PostSerializer
from django.urls import reverse
from django.contrib.auth import get_user_model
from shared_helpers import create_test_user

from views.view_test_base import ViewTestBase

def create_test_post_from_user(user): 
    post = Post.objects.create(
        author=user, 
        text="Test"
    )
    Comment.objects.create(
        author=create_test_user(), 
        post=post, 
        text="Test Comment for Test Post", 
    )
    return post

class TestPostsViewSet(ViewTestBase): 
    def setUp(self): 
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username="test_user", password="12345"
        )
        self.post1 = create_test_post_from_user(self.user) 
        self.post2 = create_test_post_from_user(self.user) 
        self.post3 = create_test_post_from_user(self.user) 
    
    def test_list(self): 
        expected_posts = [self.post3, self.post2, self.post1] # the most recent first
        expected_response = {
            'posts': PostSerializer(expected_posts, many=True).data
        }
        url = reverse("posts-list") + f'?profile_id={self.user.pk}' 
        self.request_test(url, self.client.get, {}, expected_response, 200)
    def test_list_without_profile_id(self): 
        url = reverse("posts-list") 
        expected_response = {
            'detail': "You must pass in profile_id as a query parameter.",
        } 
        self.request_test(url, self.client.get, {}, expected_response, 401) 
    def test_list_of_non_existing_user(self): 
        url = reverse("posts-list") + f'?profile_id={4242}' 
        expected_response = {
            'detail': "Not found."
        }
        self.request_test(url, self.client.get, {}, expected_response, 404)

    def test_create(self): 
        new_user = self.sign_in_random_user()
        data = {
            'text': "New post of new_user"
        }
        url = reverse("posts-list")

        response = self.request_test(url, self.client.post, data, None, 200) 
        # verify response 
        self.assertEqual(
            PostSerializer(Post.objects.get(pk=response['pk'])).data, 
            response
        )
        # verify post was created 
        new_user_posts = Post.objects.filter(author=new_user) 
        self.assertEqual(
            new_user_posts.count(), 
            1
        ) 
        self.assertEqual(
            new_user_posts.first().text, 
            data['text']
        )
    def test_create_not_logged_in(self): 
        data = {
            "text": "New post"
        }
        url = reverse("posts-list")
        expected_response = {
            'detail': 'Authentication credentials were not provided.'
        } 
        self.request_test(url, self.client.post, data, expected_response, 401)
    


    def test_update(self): 
        self.client.login(username=self.user.username, password="12345")
        test_post_pk = self.post1.pk
        data = {
            "text": "Updated text", 
        }
        url = reverse("posts-detail", kwargs={
            'pk': test_post_pk, 
        })
        response  = self.request_test(url, self.client.put, data, None, 200)
        # verify response 
        self.assertEqual(
            PostSerializer(Post.objects.get(pk=test_post_pk)).data, 
            response,
        )
        # verify post was updated 
        self.assertEqual(
            Post.objects.get(pk=test_post_pk).text,
            data['text']
        )
    def test_update_from_non_author(self): 
        user = self.sign_in_random_user() 
        test_post_pk = self.post1.pk 
        data = {
            "text": "Updated text", 
        }
        url = reverse("posts-detail", kwargs={
            'pk': test_post_pk, 
        })
        self.request_test(url, self.client.put, data, None, 403)
        # verify post was NOT updated 
        self.assertEqual(
            Post.objects.get(pk=test_post_pk).text, 
            self.post1.text,
        )
    def test_update_404_for_non_existing_post(self): 
        user = self.sign_in_random_user() 
        test_post_pk = 424242 
        data = {
            "text": "Updated text"
        }
        url = reverse("posts-detail", kwargs={
            'pk': test_post_pk, 
        })
        expected_response = {
            'detail': 'Not found.'
        }
        self.request_test(url, self.client.put, data, expected_response, 404)

    def test_destroy(self): 
        self.client.login(username=self.user.username, password="12345") 
        test_post_pk = self.post1.pk 
        url = reverse("posts-detail", kwargs={
            'pk': test_post_pk 
        })
        self.request_test(url, self.client.delete, {}, {}, 200)
        # verify post was deleted 
        self.assertEqual(
            Post.objects.filter(pk=test_post_pk).count(), 
            0
        )
    def test_destroy_from_non_author(self): 
        user = self.sign_in_random_user() 
        test_post_pk = self.post1.pk 
        url = reverse("posts-detail", kwargs={
            'pk': test_post_pk
        })
        self.request_test(url, self.client.delete, {}, {}, 403)
        # verify post was NOT deleted 
        self.assertEqual(
            Post.objects.filter(pk=test_post_pk).count(), 
            1
        )
    def test_destroy_404_for_non_existing_post(self): 
        user = self.sign_in_random_user() 
        test_post_pk = 424242 
        url = reverse("posts-detail", kwargs={
            'pk': test_post_pk
        })
        expected_response = {
            'detail': 'Not found.'
        }
        self.request_test(url, self.client.delete, {}, expected_response, 404)
    
    def test_like(self): 
        user = self.sign_in_random_user() 
        test_post_pk = self.post1.pk 
        url = reverse("posts-like", kwargs={
            'pk': test_post_pk
        })
        self.request_test(url, self.client.post, {}, {}, 200)
        # verify like was added 
        self.assertEqual(
            list(self.post1.liked_by.users_who_liked.all()), 
            [user]
        )
    def test_like_yourself(self): 
        self.client.login(username=self.user.username, password="12345")
        url = reverse("posts-like", kwargs={
            'pk': self.post1.pk
        })
        expected_response = { 
            'detail': "You cannot like your own content."
        }
        self.request_test(url, self.client.post, {}, expected_response, 405)
        # verify like was not added 
        self.assertEqual(
            self.post1.liked_by.count(), 
            0
        )
    def test_like_on_non_existing_post(self): 
        self.sign_in_random_user() 
        test_post_pk = 424242 
        url = reverse("posts-like", kwargs={
            'pk': test_post_pk
        }) 
        expected_response = {
            'detail': 'Not found.'
        }
        self.request_test(url, self.client.post, {}, expected_response, 404)
    def test_like_while_not_signed_in(self): 
        test_post_pk = self.post1 
        url = reverse("posts-like", kwargs={
            'pk': test_post_pk
        })
        expected_response = {
            'detail': 'Authentication credentials were not provided.'
        }
        self.request_test(url, self.client.post, {}, expected_response, 401)


    



