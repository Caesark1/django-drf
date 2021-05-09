from django.test import TestCase

from store.serializers import BookSerializer
from store.models import Book


class BookSerializerTestCase(TestCase):
    def test_serializer(self):
        book1 = Book.objects.create(
            title='Test Book',
            price=100.23
        )
        book2 = Book.objects.create(
            title='Test Book2',
            price=150.99
        )
        serializer_data = BookSerializer([book1, book2], many=True).data
        expected_data = [
            {
                'id': book1.id,
                'title': book1.title,
                'price': "100.23"
            },
            {
                'id': book2.id,
                'title': book2.title,
                'price': "150.99"
            }
        ]
        self.assertEqual(expected_data, serializer_data)