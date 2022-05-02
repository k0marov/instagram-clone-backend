from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response 
import rest_framework.permissions as permissions
from rest_framework.decorators import action 

from instagram_app.models import Post, Comment
from instagram_app.serializers import CommentSerializer


class CommentsViewSet(ViewSet): 
    def get_permissions(self): 
        if self.action == "list": 
            return [] 
        else: 
            return [permissions.IsAuthenticated()] 
    def list(self, request, profile_pk=None, post_pk=None): 
        post = get_object_or_404(Post, pk=post_pk) 
        comments = post.comments
        serializer = CommentSerializer(comments, many=True) 
        return Response(serializer.data, 200)
    def create(self, request, profile_pk=None, post_pk=None): 
        post = get_object_or_404(Post, pk=post_pk) 
        text = request.data['text']
        Comment.objects.create(
            author=request.user, 
            post=post, 
            text=text
        )
        return Response(status=200)

    @action(detail=True, methods=["POST"], url_name="like")
    def like(self, request, profile_pk=None, post_pk=None, pk=None): 
        comment = get_object_or_404(Comment, pk=pk)
        liked_successfuly = comment.liked_by.add_like_from(request.user) 
        if not liked_successfuly: 
            return Response({
                'detail': "You cannot like your own content."
            }, status=405)
        else: 
            return Response(status=200)