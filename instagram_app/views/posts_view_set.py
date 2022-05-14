from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response 
from django.http import HttpRequest
import rest_framework.permissions as permissions
from django.contrib.auth import get_user_model
from rest_framework.decorators import action 

from instagram_app.serializers import PostSerializer
from instagram_app.models import Post

class PostsViewSet(ViewSet): 
    def get_permissions(self): 
        if self.action == "list": 
            return [] 
        else: 
            return [permissions.IsAuthenticated()] 

    def list(self, request): 
        profile_id = request.query_params.get('profile_id') 
        if profile_id is None: 
            return Response({'detail': 'You must pass in profile_id as a query parameter.'}, 401)
        author = get_object_or_404(get_user_model(), pk=profile_id)
        posts = Post.objects.filter(author=author) 
        serializer = PostSerializer(posts, many=True) 
        response = {
            'posts': serializer.data
        }
        return Response(response, status=200)

    def create(self, request: HttpRequest, profile_pk=None): 
        """Create a new post (author is the logged in user)"""
        text = request.data["text"]
        new_post = Post.objects.create(
            author=request.user,
            text=text, 
        )
        response = PostSerializer(new_post).data
        return Response(response, status=200)

    def update(self, request, pk=None): 
        """Edit an existing post (author must be the logged in user)"""
        text = request.data["text"] 
        post = get_object_or_404(Post, pk=pk) 
        if post.author != request.user:
            return Response(status=403)
        post.text = text 
        post.save() 
        response = PostSerializer(post).data
        return Response(response, status=200)

    def destroy(self, request, pk=None): 
        """Delete an existing post (author must be the logged in user)"""
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user:
            return Response(status=403)
        post.delete() 
        return Response(status=200)

    @action(detail=True, methods=["POST"], url_name="like")
    def like(self, request, profile_pk=None, pk=None): 
        post = get_object_or_404(Post, pk=pk)
        liked_successfully = post.liked_by.add_like_from(request.user)
        if not liked_successfully: 
            return Response({
                'detail': "You cannot like your own content."
            }, 405)
        else: 
            return Response(status=200)


    
