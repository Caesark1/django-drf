import json
from django.db.models.aggregates import Avg, Count
from django.db.models.expressions import Case, F, When

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username='testusername',
        )
        self.user2 = User.objects.create(
            username='testusername2',
        )
        self.url = reverse('book-list')
        Book.objects.create(
            title='Test Book',
            price=100.23,
            discount=50.00,
            author_name='Willi Wonko',
            owner=self.user
        )
        Book.objects.create(
            title='Test Book2',
            price=150.99,
            discount=30,
            author_name='Mele Da',
        )
        Book.objects.create(
            title='Something',
            price=150.99,
            author_name='Mele Da',
        )
        self.book1 = Book.objects.get(title='Test Book')
        self.book2 = Book.objects.get(title='Test Book2')
        self.book3 = Book.objects.get(title='Something')
        UserBookRelation.objects.create(user=self.user, book=self.book1, like=True, rate=5)
        

    def test_get(self):
        response = self.client.get(self.url)
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
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['price_after_discount'], '50.23')
        self.assertEqual(serializer_data[0]['likes_count'], 1)
        self.assertEqual(serializer_data[0]['annotated_like'], 1)

    def test_get_filter(self):
        response = self.client.get(self.url, data={'price': 150.99})
        books = Book.objects.filter(id__in=[self.book2.id, self.book3.id]).annotate(
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
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        books = Book.objects.filter(id__in=[self.book1.id, self.book2.id]).annotate(
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
        response = self.client.get(self.url, data={'search': 'Test Book'})
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data, response.data)

    def test_get_ordering(self):
        response = self.client.get(self.url, data={'ordering': 'price'})
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
            ).order_by('price')
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
    
    def test_create(self):
        books_in_db_before_create = Book.objects.all().count()
        data = {
            'title': 'Some Test Book',
            'price': '100',
            'author_name': 'Some Author name',
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=json_data, 
                                            content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.content)
        self.assertEqual(self.user, Book.objects.last().owner)
        self.assertNotEqual(4, books_in_db_before_create)
    
    def test_update(self):
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            'title': self.book1.title,
            'price': '150',
            'author_name': self.book1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, 
                                            content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content)
        self.book1.refresh_from_db()
        self.assertEqual(150, self.book1.price)
    
    def test_update_not_owner(self):
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            'title': self.book1.title,
            'price': '150',
            'author_name': self.book1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, 
                                            content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, response.content)
        self.assertEqual({'detail': 
        ErrorDetail(
            string='You do not have permission to perform this action.', 
            code='permission_denied')
        }, response.data)
    

class BooksRelationTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username='testusername',
        )
        self.user2 = User.objects.create(
            username='testusername2',
        )
        Book.objects.create(
            title='Test Book',
            price=100.23,
            author_name='Willi Wonko',
            owner=self.user
        )
        Book.objects.create(
            title='Test Book2',
            price=150.99,
            author_name='Mele Da',
            owner=self.user
        )
        Book.objects.create(
            title='Something',
            price=150.99,
            author_name='Mele Da',
            owner=self.user
        )
        self.book1 = Book.objects.get(title='Test Book')
        self.book2 = Book.objects.get(title='Test Book2')
        self.book3 = Book.objects.get(title='Something')
        self.url = reverse('userbookrelation-detail', args=(self.book1.id,))

    def test_like(self):
        data = {
            'like': True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(self.url, data=json_data,
                                    content_type='application/json')
        userbookrelation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.book1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(userbookrelation.like)
    
    def test_in_bookmarks(self):
        data = {
            'in_bookmarks': True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(self.url, data=json_data,
                                    content_type='application/json')
        userbookrelation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.book1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(userbookrelation.in_bookmarks)
    
    def test_rate(self):
        data = {
            'rate': 5,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(self.url, data=json_data,
                                    content_type='application/json')
        userbookrelation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.book1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(5, userbookrelation.rate)
