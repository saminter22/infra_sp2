# api/views.py
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
# from rest_framework.pagination import LimitOffsetPagination

from reviews.models import User, Title, Genre, Category, Review
from api_yamdb.settings import (DEFAULT_CHAR_FIELD_LENGTH, ADMIN_EMAIL)
from .serializers import (UserSerializer, UserEditSerializer,
                          UserRegisterationSerializer, UserTokenSerializer,
                          TitleReadSerializer, TitleUpdateSerializer,
                          GenreSerializer, CategorySerializer,
                          CommentSerializer, ReviewSerializer)
from .permissions import (IsAuthenticatedAndAdmin, IsAuthorCanUpdateOrReadOnly,
                          ReadIfNotAdmin)
from .utils import FilterTitle, MixinBasicSet


def create_and_send_registration_email(email_to, confirmation_code):
    email_subject = 'Регистрация'
    email_message = f'Код подтверждения: {confirmation_code}'
    email_recipient_list = [email_to]
    send_mail(
        subject=email_subject,
        message=email_message,
        from_email=ADMIN_EMAIL,
        recipient_list=email_recipient_list,
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def registerate(request):
    """Регистрирует нового пользователя."""
    serializer = UserRegisterationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_name = serializer.validated_data['username']
    user_email = serializer.validated_data['email']
    serializer.save()
    confirmation_code = get_random_string(length=DEFAULT_CHAR_FIELD_LENGTH)
    User.objects.filter(
        username=user_name,
        email=user_email).update(confirmation_code=confirmation_code)
    create_and_send_registration_email(email_to=user_email,
                                       confirmation_code=confirmation_code)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    """Получение токена в обмен  confirmation code."""
    serializer = UserTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_name = serializer.initial_data['username']
    confirmation_code = serializer.initial_data['confirmation_code']
    user_obj = get_object_or_404(User, username=user_name)
    if user_obj.confirmation_code != confirmation_code:
        user_obj.confirmation_code = get_random_string(
            length=DEFAULT_CHAR_FIELD_LENGTH)
        user_obj.save()
        message = {'confirmation_code': 'Неверный код'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user_obj)
    message = {'token': str(refresh.access_token)}
    return Response(message, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Класс для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedAndAdmin]
    filter_backends = (filters.SearchFilter, )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'

    @action(detail=False,
            methods=['PATCH', 'GET'],
            permission_classes=(permissions.IsAuthenticated, ))
    def me(self, request):
        user_obj = get_object_or_404(User, id=request.user.id)
        if request.method == 'GET':
            return Response(UserSerializer(user_obj).data,
                            status=status.HTTP_200_OK)

        serializer = UserEditSerializer(
            instance=user_obj,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user_obj.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (ReadIfNotAdmin, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = FilterTitle
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleReadSerializer
        return TitleUpdateSerializer


class CategoryViewSet(MixinBasicSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (ReadIfNotAdmin, )


class GenreViewSet(MixinBasicSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (ReadIfNotAdmin, )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorCanUpdateOrReadOnly, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorCanUpdateOrReadOnly, )

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
