# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    registerate,
    get_token,
    UserViewSet,
    TitleViewSet,
    GenreViewSet,
    CategoryViewSet,
    ReviewViewSet,
    CommentViewSet
)


v1_router = DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('titles', TitleViewSet)
v1_router.register('genres', GenreViewSet)
v1_router.register('categories', CategoryViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', registerate, name='signup'),
    path('v1/auth/token/', get_token, name='token'),
    path('v1/', include(v1_router.urls)),
]
