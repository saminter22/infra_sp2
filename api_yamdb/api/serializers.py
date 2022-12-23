# api/serializers.py
import datetime as dt
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import User
from reviews.utils import check_username
from api_yamdb.settings import (
    DEFAULT_CHAR_FIELD_LENGTH,
    DEFAULT_EMAIL_FIELD_LENGTH,
)

from reviews.models import Title, Genre, Category, Review, Comment


USER_MODEL_FIELDS = (
    'username',
    'email',
    'role',
    'first_name',
    'last_name',
    'bio',
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = USER_MODEL_FIELDS


class UserEditSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = USER_MODEL_FIELDS
        read_only_fields = (
            'role',
        )


class UserRegisterationSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=DEFAULT_CHAR_FIELD_LENGTH,
    )
    email = serializers.EmailField(
        required=True,
        max_length=DEFAULT_EMAIL_FIELD_LENGTH,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )

    def validate(self, data):
        user_name = data.get('username')
        user_email = data.get('email')
        found_by_username = User.objects.filter(username=user_name)
        found_by_email = User.objects.filter(email=user_email)
        error_username = check_username(user_name)
        if error_username:
            raise serializers.ValidationError(
                error_username
            )
        if found_by_username:
            raise serializers.ValidationError(
                'Пользователь с таким именем пользователя уже существует!'
            )
        if found_by_email:
            raise serializers.ValidationError(
                'Пользователь с таким адресом эл. почты уже существует!'
            )
        return data


class UserTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=DEFAULT_CHAR_FIELD_LENGTH,
    )
    confirmation_code = serializers.CharField(
        required=True,
        max_length=DEFAULT_CHAR_FIELD_LENGTH,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code',
        )


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    category = CategorySerializer(
        read_only=True
    )
    rating = serializers.IntegerField(
        read_only=True,
        required=False,
        max_value=10,
        min_value=1,
    )

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        if value > dt.datetime.now().year:
            raise serializers.ValidationError(
                "Год выпуска не может быть больше текущего!"
            )
        return value


class TitleUpdateSerializer(TitleReadSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        fields = '__all__'
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        many=False
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('id', 'pub_date', 'review',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        many=False
    )

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('id', 'pub_date', 'title',)

    def validate(self, data):
        user = get_object_or_404(User, username=self.context['request'].user)
        title_id = self.context['view'].kwargs.get('title_id')
        is_review = Review.objects.filter(
            author=user,
            title=title_id
        ).exists()

        if is_review and self.context['request'].method == 'POST':
            raise serializers.ValidationError(
                'Пользователь может оставить '
                'только один отзыв на произведение.'
            )
        return data
