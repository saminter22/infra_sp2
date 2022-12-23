from django_filters.rest_framework import FilterSet, CharFilter
from rest_framework import mixins, viewsets, filters

from reviews.models import Title
from .permissions import IsAuthorCanUpdateOrReadOnly


class FilterTitle(FilterSet):
    genre = CharFilter(field_name='genre__slug', lookup_expr='iexact')
    category = CharFilter(field_name='category__slug', lookup_expr='iexact')
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = (
            'name',
            'category',
            'genre',
            'year',
        )


class MixinBasicSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthorCanUpdateOrReadOnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'
