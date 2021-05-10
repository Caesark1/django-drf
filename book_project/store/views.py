from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_fields = ['price']
    search_fields = ['title', 'author_name']
    ordering_fields = ['price', 'author_name']


def auth(request):
    return render(request, 'OAuth.html')


# var xsrfCookie = postman.getResponseCookie("csrftoken"); 
# postman.setEnvironmentVariable('csrftoken', xsrfCookie.value);