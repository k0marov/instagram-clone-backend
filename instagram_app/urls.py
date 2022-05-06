from django.urls import include, path 
from rest_framework import routers 
from rest_framework_nested import routers as nested_routers
from rest_framework.authtoken.views import obtain_auth_token

import instagram_app.views as views


profile_router = routers.DefaultRouter() 
profile_router.register(r'profiles', views.ProfilesViewSet, basename="profiles") 
# generates 
# /profiles/{pk}/ 
# /profiles-me/
# /profiles-avatar/

posts_router = nested_routers.NestedSimpleRouter(
    profile_router, 
    r'profiles', 
    lookup='profile'
)
posts_router.register(r'posts', views.PostsViewSet, basename='posts')
# generates 
# /profiles/{profile_pk}/posts/ 
# /profiles/{profile_pk}/posts/{post_pk}/ 
# /profiles/{profile_pk}/posts-like/{post_pk}/

comments_router = nested_routers.NestedSimpleRouter(
    posts_router, 
    r'posts', 
    lookup='post', 
)
comments_router.register(r'comments', views.CommentsViewSet, basename='comments') 
# generates 
# /profiles/{profile_pk}/posts/{post_pk}/comments/
# /profiles/{profile_pk}/posts/{post_pk}/comments/{pk}/
# /profiles/{profile_pk}/posts/{post_pk}/comments-like/{pk}/



urlpatterns = [
    path('', include(profile_router.urls)),
    path('', include(posts_router.urls)),
    path('', include(comments_router.urls)),
    path('api-token-login/', obtain_auth_token, name="api-token-login"),
    path('api-token-register/', views.TokenRegisterView.as_view(), name="api-token-register"),
]