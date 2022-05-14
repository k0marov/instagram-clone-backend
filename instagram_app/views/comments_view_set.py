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
    def list(self, request): 
        post_pk = request.query_params.get("post_id")
        if post_pk is None: 
            response = {
                'detail': "You need to provide the post_id query parameter."
            }
            return Response(response, 400) 
        post = get_object_or_404(Post, pk=post_pk) 
        comments = post.comments
        response = {
            "comments": CommentSerializer(comments, many=True).data
        }
        return Response(response, 200)
    def create(self, request): 
        post_pk = request.query_params.get("post_id") 
        if post_pk is None: 
            response = {
                'detail': "You need to provide the post_id query parameter."
            }
            return Response(response, 400) 
        post = get_object_or_404(Post, pk=post_pk) 
        text = request.data['text']
        new_comment = Comment.objects.create(
            author=request.user, 
            post=post, 
            text=text
        )
        response = CommentSerializer(new_comment).data
        
        return Response(response, status=200)

    @action(detail=True, methods=["POST"], url_name="like")
    def like(self, request, pk=None): 
        comment = get_object_or_404(Comment, pk=pk)
        liked_successfuly = comment.liked_by.add_like_from(request.user) 
        if not liked_successfuly: 
            return Response({
                'detail': "You cannot like your own content."
            }, status=405)
        else: 
            return Response(status=200)