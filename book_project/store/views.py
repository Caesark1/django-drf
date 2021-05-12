from django.db.models.aggregates import Avg, Count
from django.db.models.expressions import Case, ExpressionWrapper, F, When
from django.db.models.fields import DecimalField
from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.mixins import UpdateModelMixin

from .models import Book, UserBookRelation
from .serializers import BookSerializer, UserBookRelationSerializer
from .permissions import IsOwnerOrReadOnly


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().annotate(
            annotated_like=Count(
                Case(
                    When(
                        userbookrelation__like=True, 
                        then=1
                        )
                    )
                ),
            rating=Avg(
                'userbookrelation__rate'
                ),
            price_after_discount=ExpressionWrapper(F('price') - F('discount'), output_field=DecimalField())
            ).order_by('id')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_fields = ['price']
    search_fields = ['title', 'author_name']
    ordering_fields = ['price', 'author_name']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()
        return super().perform_create(serializer)
    

class UserBookRelationView(UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                        book_id=self.kwargs['book'])
        return obj


def auth(request):
    return render(request, 'OAuth.html')


# var xsrfCookie = postman.getResponseCookie("csrftoken"); 
# postman.setEnvironmentVariable('csrftoken', xsrfCookie.value);