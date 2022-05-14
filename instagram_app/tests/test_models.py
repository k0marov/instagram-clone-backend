"""Test all models"""
from abc import abstractmethod
import setup_django
setup_django.setup_tests()

from django.test import TestCase
import datetime  
from instagram_app.models import (
    Profile, 
    Post, 
    PostLikes, 
    Comment, 
    CommentLikes, 
) 

from shared_helpers import create_test_user
from instagram_app.shared import serialize_datetime
from rest_framework.authtoken.models import Token


class TestTokenAuth(TestCase): 
    def test_token_should_be_created(self): 
        user = create_test_user() 
        print(Token.objects)
        self.assertNotEqual(
            Token.objects.get(user=user),
            None
        )

class TestProfile(TestCase): 
    def test_autocreate(self): 
        test_user = create_test_user() 
        self.assertEqual(
            type(test_user.profile), Profile
        )
    def test_username(self): 
        test_user = create_test_user() 
        self.assertEqual(
            test_user.profile.username, 
            test_user.username, 
        )


class AbstractTestLikesList: 
    """
    This class is abstract, 
    it should be subclassed to test LikesList in models 
    which have an AbstractLikesList subclass as a field"""
    @abstractmethod
    def get_likes_list(self): 
        pass 
    def test_liked_by_count(self): 
        liked_by = self.get_likes_list() 
        self.assertEqual(liked_by.count(), 0)
        liked_by.users_who_liked.add(create_test_user()) 
        self.assertEqual(liked_by.count(), 1)
    def test_liked_by_add_like(self): 
        liked_by = self.get_likes_list()
        liked_by.add_like_from(create_test_user()) 
        self.assertEqual(liked_by.users_who_liked.count(), 1)

    def test_liked_by_add_selflike(self): 
        '''liking your own post should not count'''
        liked_by = self.get_likes_list() 
        liked_by.add_like_from(liked_by.get_liked_object_author())
        self.assertEqual(liked_by.users_who_liked.count(), 0)


class TestPost(TestCase, AbstractTestLikesList): 
    def setUp(self): 
        self.test_post = Post.objects.create(
            author=create_test_user(),
            text="A test post"
        ) 
    # override
    def get_likes_list(self): 
        return self.test_post.liked_by


    def test_autocreate_created_at(self): 
        self.assertEqual(
            self.test_post.created_at.date(), datetime.date.today()
        )
    def test_autocreate_liked_by(self): 
        self.assertEqual(
            type(self.test_post.liked_by), PostLikes
        )
    def test_liked_by_author(self): 
        self.assertEqual(
            self.test_post.liked_by.get_liked_object_author(), 
            self.test_post.author
        )
    def test_serialize_created_at(self): 
        self.assertEqual(
            self.test_post.serialize_created_at(), 
            serialize_datetime(self.test_post.created_at)            
        )

class TestComment(TestCase, AbstractTestLikesList): 
    def setUp(self): 
        self.post = Post.objects.create(
            author=create_test_user(), 
            text="A test post"
        )
        self.comment = Comment.objects.create(
            post=self.post, 
            author=create_test_user(), 
            text="A test comment"
        )
    # override
    def get_likes_list(self):
        return self.comment.liked_by 

    def test_autocreate_created_at(self): 
        self.assertEqual(
            self.comment.created_at.date(), datetime.date.today()
        )
    def test_autocreate_liked_by(self): 
        self.assertEqual(
            type(self.comment.liked_by), CommentLikes
        )
    def test_liked_by_author(self): 
        self.assertEqual(
            self.comment.liked_by.get_liked_object_author(), 
            self.comment.author, 
        )
    def test_serialize_created_at(self): 
        self.assertEqual(
            self.comment.serialize_created_at(), 
            serialize_datetime(self.comment.created_at)
        )