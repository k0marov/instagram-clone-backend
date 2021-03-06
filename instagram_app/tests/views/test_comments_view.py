from instagram_app.tests.shared_helpers import create_test_profile
from setup_django import setup_tests 
setup_tests()

from instagram_app.serializers import CommentSerializer
from django.contrib.auth import get_user_model
from views.view_test_base import ViewTestBase 
from instagram_app.models import Post, Comment
from shared_helpers import create_test_user
from django.urls import reverse

class TestCommentsViewSet(ViewTestBase): 
    def setUp(self): 
        super().setUp() 
        self.user = get_user_model().objects.create_user(
            username="test_user", password="12345"
        )
        self.post = Post.objects.create(
            author=self.user.profile, 
            text="Test Post Text"
        )
        self.comment1 = Comment.objects.create(
            post=self.post, 
            author=create_test_profile(), 
            text="test comment 1"
        )
        self.comment2 = Comment.objects.create(
            post=self.post, 
            author=create_test_profile(), 
            text="test comment 2"
        )
    def test_list(self): 
        url = reverse("comments-list") + f"?post_id={self.post.pk}"
        comments = [self.comment2, self.comment1] # most recent first
        expected_response = {
            "comments": CommentSerializer(comments, many=True).data 
        }
        self.request_test(url, self.client.get, {}, expected_response, 200)
    def test_list_without_post_id(self): 
        url = reverse("comments-list") 
        expected_response = {
            'detail': "You need to provide the post_id query parameter."
        }
        self.request_test(url, self.client.get, {}, expected_response, 400)
    def test_list_404(self): 
        url = reverse("comments-list") + f"?post_id={4242}"
        expected_response = {
            "detail": "Not found."
        }
        self.request_test(url, self.client.get, {}, expected_response, 404)

    def test_like(self): 
        user = self.sign_in_random_user()
        test_comment_pk = self.comment1.pk
        url = reverse("comments-toggle-like", kwargs={
            'pk': test_comment_pk 
        })
        self.request_test(url, self.client.post, {}, {}, 200)
        # verify that the comment was liked 
        self.assertEqual(
            list(Comment.objects.get(pk=test_comment_pk).liked_by.users_who_liked.all()),
            [user.profile]
        )
    def test_like_404(self): 
        self.sign_in_random_user()
        url = reverse("comments-toggle-like", kwargs={
            'pk': 424242, 
        })
        expected_response = {
            'detail': 'Not found.'
        }
        self.request_test(url, self.client.post, {}, expected_response, 404)
    def test_like_unauthorized(self): 
        url = reverse("comments-toggle-like", kwargs={
            'pk': self.comment1.pk
        })
        expected_response = {
            "detail": "Authentication credentials were not provided."
        }
        self.request_test(url, self.client.post, {}, expected_response, 401) 
    def test_like_yourself(self): 
        self.client.login(username=self.user.username, password="12345")
        comment = Comment.objects.create(
            post=self.post, 
            author=self.user.profile, 
            text="Some new comment"
        )
        url = reverse("comments-toggle-like", kwargs={
            'pk': comment.pk
        })
        expected_response = {
            'detail': "You cannot like your own content."
        }
        self.request_test(url, self.client.post, {}, expected_response, 405)
        # verify comment was not liked 
        self.assertEqual(
            Comment.objects.get(pk=self.comment1.pk).liked_by.count(), 
            0
        )

    def test_create(self): 
        self.sign_in_random_user() 
        data = {
            'text': "New comment"
        }
        new_post = Post.objects.create(
            author=self.user.profile, 
            text="Some test post"
        )
        url = reverse("comments-list") + f"?post_id={new_post.pk}"
        response = self.request_test(url, self.client.post, data, None, 200)
        # verify response 
        self.assertEqual(
            CommentSerializer(Comment.objects.get(pk=response['pk'])).data, 
            response
        )
        # verify comment was created 
        self.assertEqual(
            new_post.comments.count(),
            1
        )
        self.assertEqual(
            Post.objects.get(pk=new_post.pk).comments.first().text, 
            data['text']
        )
    def test_create_without_post_parameter(self): 
        self.sign_in_random_user()
        url = reverse("comments-list") 
        expected_response = {
            'detail': "You need to provide the post_id query parameter."
        }
        self.request_test(url, self.client.post, {}, expected_response, 400)
    def test_create_404_non_existing_post(self): 
        self.sign_in_random_user()
        data = {
            'text': 'some new comment'
        }
        url = reverse("comments-list") + f"?post_id={4242}"
        expected_response = {
            'detail': 'Not found.'
        }
        self.request_test(url, self.client.post, data, expected_response, 404)
    def test_create_unauthorized(self):
        data = {
            'text': 'some new comment'
        }
        url = reverse("comments-list") + f"?post_id={self.post.pk}"
        expected_response = {
            "detail": "Authentication credentials were not provided."
        }
        self.request_test(url, self.client.post, data, expected_response, 401)
        





        
