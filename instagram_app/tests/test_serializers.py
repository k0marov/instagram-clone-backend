"""Test all serializers"""
from instagram_app.tests.shared_helpers import get_fixtures_path
import setup_django
setup_django.setup_tests()

from abc import abstractmethod
from pathlib import Path
from django.test import TestCase
from django.core.files import File
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from instagram_app.serializers import (
    CommentSerializer, 
    LikedListSerializer, 
    PostSerializer, 
    ProfileSerializer, 
    UserSerializer
)
from instagram_app.models import Post, Comment

from shared_helpers import create_test_user

def create_test_post(): 
    return Post.objects.create(
        author=create_test_user(), 
        text="Test Post",
    )
def create_test_comment(post): 
    return Comment.objects.create(
        author=create_test_user(), 
        post=post, 
        text="Test Comment", 
    )

class TestUserSerializer(TestCase): 
    def test_should_validate_properly_good(self): 
        data = {
            'username': 'test-username', 
            'password': '12345', 
        }
        serializer = UserSerializer(data=data) 
        self.assertTrue(
            serializer.is_valid()
        )
    def test_should_validate_properly_error(self): 
        data = {
            'username': 'no-password'
        }
        serializer = UserSerializer(data=data) 
        self.assertFalse(
            serializer.is_valid()
        )
    def test_should_create_user(self): 
        data = {
            'username': 'test-username', 
            'password': '12345' 
        } 
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_user_pk = serializer.save().pk
        new_user = get_user_model().objects.get(pk=new_user_pk) 
        self.assertEqual(
            new_user.username, 
            'test-username', 
        )
        self.assertTrue(
            check_password('12345', new_user.password)
        )

class TestProfileSerializer(TestCase): 
    def setUp(self): 
        self.user = create_test_user() 
        self.profile = self.user.profile 

        self.profile.about = "Some profile info"
        with Path(get_fixtures_path() + "test_avatar.png").open(mode="rb") as f: 
            self.profile.avatar = File(f, name='test_avatar.png')
            self.profile.save()

        self.follower1 = create_test_user().profile
        self.follower2 = create_test_user().profile

        self.profile.followers.add(self.follower1) 
        self.profile.followers.add(self.follower2)  

        self.follower1.followers.add(self.profile) 
        self.follower2.followers.add(self.profile)
        
        self.serializer = ProfileSerializer(instance=self.profile) 
        self.serialized_data = self.serializer.data
    def test_pk(self): 
        self.assertEqual(
            self.serialized_data['pk'], 
            self.profile.pk, 
        )
    def test_username(self): 
        self.assertEqual(
            self.serialized_data['username'], self.user.username, 
        )
    def test_about(self): 
        self.assertEqual(
            self.serialized_data['about'], self.profile.about
        )
    def test_avatar(self): 
        self.assertEqual(
            self.serialized_data['avatar'], self.profile.avatar.url
        )
    def test_followers(self): 
        self.assertEqual(
            self.serialized_data['followers'], 
            2
        )
    def test_follows(self): 
        self.assertEqual(
            self.serialized_data['follows'],
            2
        )
    def test_avatar_url(self): 
        self.assertTrue(
            self.serialized_data['avatar'].startswith("/media/avatars/user_" + str(self.user.pk)), 
        )

class TestPostSerializer(TestCase): 
    def setUp(self): 
        self.post = create_test_post() 
        self.post.liked_by.add_like_from(create_test_user())
        create_test_comment(post=self.post)
        self.serializer = PostSerializer(instance=self.post)
        self.serialized_data = self.serializer.data
    def test_pk(self): 
        self.assertEqual(
            self.serialized_data['pk'], 
            self.post.pk
        )
    def test_liked_by(self): 
        self.assertEqual(
            type(self.serializer.fields.get("liked_by")), 
            LikedListSerializer
        )
    def test_author(self): 
        self.assertEqual(
            self.serialized_data['author'], self.post.author.username
        )
    def test_created_at(self): 
        self.assertEqual(
            self.serialized_data['created_at'], 
            self.post.serialize_created_at() 
        )
    def test_text(self): 
        self.assertEqual(
            self.serialized_data['text'], 
            self.post.text,
        )
    def test_comments(self): 
        self.assertEqual(
            type(self.serializer.fields.get('comments').child), 
            CommentSerializer
        )

class TestCommentSerializer(TestCase): 
    def setUp(self): 
        self.post = create_test_post() 
        self.comment = create_test_comment(post=self.post)
        self.comment.liked_by.add_like_from(create_test_user()) 
        self.serializer = CommentSerializer(instance=self.comment)
        self.serialized_data = self.serializer.data
    def test_pk(self): 
        self.assertEqual(
            self.serialized_data['pk'], 
            self.comment.pk,
        )
    def test_author(self): 
        self.assertEqual(
            self.serialized_data['author'], 
            self.comment.author.username, 
        )
    def test_created_at(self): 
        self.assertEqual(
            self.serialized_data['created_at'], 
            self.comment.serialize_created_at(), 
        )
    def test_text(self): 
        self.assertEqual(
            self.serialized_data['text'], 
            self.comment.text, 
        )
    def test_liked_by(self): 
        self.assertEqual(
            type(self.serializer.fields.get('liked_by')), 
            LikedListSerializer
        )

class TestLikedListSerializer(TestCase): 
    def setUp(self): 
        self.post = create_test_post() 
        self.liked_list = self.post.liked_by
    def __assert_serialized_equal(self, value): 
        self.assertEqual(
            LikedListSerializer(self.liked_list).data, 
            value
        )
        
    def test_equals_zero_initially(self): 
        self.__assert_serialized_equal(0)
    def test_increments(self): 
        self.liked_list.add_like_from(create_test_user())
        self.__assert_serialized_equal(1) 
        self.liked_list.add_like_from(create_test_user()) 
        self.__assert_serialized_equal(2)
        