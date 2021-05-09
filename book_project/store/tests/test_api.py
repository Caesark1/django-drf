from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BooksAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('book-list')
        Book.objects.create(
            title='Test Book',
            price=100.23,
            author_name='Willi Wonko'
        )
        Book.objects.create(
            title='Test Book2',
            price=150.99,
            author_name='Mele Da'
        )
        Book.objects.create(
            title='Something',
            price=150.99,
            author_name='Mele Da'
        )
        self.book1 = Book.objects.get(title='Test Book')
        self.book2 = Book.objects.get(title='Test Book2')
        self.book3 = Book.objects.get(title='Something')

    def test_get(self):
        response = self.client.get(self.url)
        serializer_data = BookSerializer([self.book1, self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        response = self.client.get(self.url, data={'price': 150.99})
        serializer_data = BookSerializer([self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        response = self.client.get(self.url, data={'search': 'Test Book'})
        serializer_data = BookSerializer([self.book1, self.book2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        response = self.client.get(self.url, data={'ordering': 'price'})
        serializer_data = BookSerializer([self.book1, self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
