from django.contrib.auth import get_user_model
from rest_framework import serializers 
from .models import Post, Comment, AbstractLikesList, Profile


# for registration
class UserSerializer(serializers.ModelSerializer): 
    password = serializers.CharField(write_only=True) 
    class Meta: 
        model = get_user_model() 
        fields = ("username", "password")

    def create(self, validated_data): 
        return get_user_model().objects.create_user(
            username=validated_data['username'], 
            password=validated_data['password'], 
        )

class ProfileSerializer(serializers.ModelSerializer): 
    followers = serializers.IntegerField(source="followers.count")
    follows = serializers.IntegerField(source="follows.count")
    class Meta: 
        model = Profile 
        fields = ['pk', 'about', 'username', 'avatar', 'followers', 'follows']
        depth = 1

class LikedListSerializer(serializers.BaseSerializer): 
    def to_representation(self, instance: AbstractLikesList): 
        return instance.count() 

class CommentSerializer(serializers.ModelSerializer): 
    author = serializers.CharField(source="author.username")
    created_at = serializers.IntegerField(source="serialize_created_at")
    liked_by = LikedListSerializer(instance="liked_by")
    class Meta: 
        model = Comment 
        fields = ['pk', "author", "post", "liked_by", "created_at", "text"]

class PostSerializer(serializers.ModelSerializer): 
    author = serializers.CharField(source='author.username')
    liked_by = LikedListSerializer(instance="liked_by")
    created_at = serializers.IntegerField(source="serialize_created_at")
    comments = CommentSerializer(instance="comments", many=True)
    class Meta: 
        model = Post 
        fields = ['pk', 'author', 'liked_by', 'comments', 'created_at', 'text'] 
        depth = 1
