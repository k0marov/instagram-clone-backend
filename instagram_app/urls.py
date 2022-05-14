from django.urls import include, path 
from rest_framework import routers 
from rest_framework.authtoken.views import obtain_auth_token

import instagram_app.views as views


profile_router = routers.DefaultRouter() 
profile_router.register(r'profiles', views.ProfilesViewSet, basename="profiles") 
# generates 
# /profiles/{id}/ 
# /profiles/me/

posts_router = routers.DefaultRouter()
posts_router.register(r'posts', views.PostsViewSet, basename='posts')
# generates 
# /posts/?profile_id={X}/
# /posts/{post_id}/ 
# /posts/{post_id}/toggle-like

comments_router = routers.DefaultRouter()
comments_router.register(r'comments', views.CommentsViewSet, basename='comments') 
# generates 
# /comments/?post_id={X}/ 
# /comments/{comment_id}/
# /comments/{comment_id}/toggle-like

urlpatterns = [
    path('', include(profile_router.urls)),
    path('', include(posts_router.urls)),
    path('', include(comments_router.urls)),
    path('api-token-login/', obtain_auth_token, name="api-token-login"),
    path('api-token-register/', views.TokenRegisterView.as_view(), name="api-token-register"),
]