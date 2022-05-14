"""Module that defines all db models"""
from abc import abstractmethod
import os
from tempfile import NamedTemporaryFile
from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.files.uploadedfile import UploadedFile
from instagram_app.shared import serialize_datetime
from django.core.files import File
from django.apps import apps
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs): 
    if created: 
        Token.objects.create(user=instance)


class Profile(models.Model):
    """
    Profile Model
    defines additional user attributes
    """
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True
    )
    followers = models.ManyToManyField("self", related_name="follows", symmetrical=False)

    def avatar_path(instance, filename): 
        return f"avatars/user_{instance.user.id}/{filename}"

    avatar = models.ImageField(upload_to=avatar_path, null=True)

    def update_avatar(self, image_file: UploadedFile): 
        img_temp = NamedTemporaryFile(delete=True)
        for chunk in image_file.chunks(): 
            img_temp.write(chunk)
        self.avatar.save(image_file.name, File(img_temp), save=True)
        img_temp.close()

    @property
    def username(self): 
        return self.user.username

    about = models.CharField(max_length=1024, default="")

    @receiver(post_save, sender=get_user_model())
    def __create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)


class AbstractLikesList(models.Model):
    """
    Abstract Model that defines a list of users who liked "something" 
    Should be subclassed defining author of that "something"
    (post, comment, etc) 
    """
    users_who_liked = models.ManyToManyField(Profile)

    def count(self): 
        return self.users_who_liked.count()  

    class Meta:
        abstract = True

    @abstractmethod
    def get_liked_object_author(self):
        pass

    def toggle_like_from(self, profile: Profile):
        """Returns False and doesn't add the like if the given user is the author"""
        if profile != self.get_liked_object_author():
            if self.users_who_liked.filter(pk=profile.pk).exists(): 
                self.users_who_liked.remove(profile)
            else: 
                self.users_who_liked.add(profile)
            return True
        else: 
            return False


class Post(models.Model):
    """
    Post Model
    defines a regular post
    """
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.CharField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    '''
    reverse relationships: 
    - comments
    - liked_by
    '''

    class Meta: 
        ordering = ('-created_at',)

    def serialize_created_at(self): 
        return serialize_datetime(self.created_at)

class PostLikes(AbstractLikesList):
    post = models.OneToOneField(
        Post, 
        on_delete=models.CASCADE, 
        related_name="liked_by", 
        primary_key=True, 
    )
    def get_liked_object_author(self): 
        return self.post.author 

    @receiver(post_save, sender=Post)
    def __create_post_likes(sender, instance, created, **kwargs):
        if created:
            PostLikes.objects.create(post=instance)

class Comment(models.Model):
    """
    Comment Model
    defines a comment for some post
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    '''
    reverse relationships: 
    - liked_by
    '''

    class Meta: 
        ordering = ["-created_at"]

    def serialize_created_at(self): 
        return serialize_datetime(self.created_at)

class CommentLikes(AbstractLikesList): 
    comment = models.OneToOneField(
        Comment, 
        on_delete=models.CASCADE, 
        related_name="liked_by", 
        primary_key=True, 
    ) 
    def get_liked_object_author(self): 
        return self.comment.author 

    @receiver(post_save, sender=Comment)
    def __create_comment_likes(sender, instance, created, **kwargs): 
        if created: 
            CommentLikes.objects.create(comment=instance)
