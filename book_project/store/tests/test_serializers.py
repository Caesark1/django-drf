from django.contrib.auth.models import User
from django.db.models.aggregates import Avg
from django.db.models.expressions import F
from django.test import TestCase
from django.db.models import Count, Case, When

from store.serializers import BookSerializer
from store.models import Book, UserBookRelation


class BookSerializerTestCase(TestCase):
    def test_serializer(self):
        user = User.objects.create(
            username='testusername',
        )
        user2 = User.objects.create(
            username='testusername2',
        )
        user3 = User.objects.create(
            username='testusername3',
        )
        book1 = Book.objects.create(
            title='Test Book',
            price=100.23,
            discount=50,
            author_name='Test User',
        )
        book2 = Book.objects.create(
            title='Test Book2',
            price=150.99,
            discount=30.99,
            author_name='Test User2',
        )

        UserBookRelation.objects.create(user=user, book=book1, like=True, rate=4,)
        UserBookRelation.objects.create(user=user2, book=book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=book1, like=True, rate=4)

        UserBookRelation.objects.create(user=user, book=book2, like=True, rate=5,)
        UserBookRelation.objects.create(user=user2, book=book2, like=True, rate=3)
        UserBookRelation.objects.create(user=user3, book=book2, like=False)

        books = Book.objects.all().annotate(
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
            price_after_discount=F('price') - F('discount')
            ).order_by('id')

        serializer_data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': book1.id,
                'title': 'Test Book',
                'price': '100.23',
                'author_name': 'Test User',
                'likes_count': 3,
                'annotated_like': 3,
                'rating': '4.33',
                'price_after_discount': '50.23'
            },
            {
                'id': book2.id,
                'title': 'Test Book2',
                'price': '150.99',
                'author_name': 'Test User2',
                'likes_count': 2,
                'annotated_like': 2,
                'rating': '4.00',
                'price_after_discount': '120.00'
            }
        ]
        self.assertEqual(expected_data, serializer_data)
