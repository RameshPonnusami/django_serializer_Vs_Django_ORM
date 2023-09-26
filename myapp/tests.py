from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer
from django.db.models.functions import Cast
from django.db.models import  CharField
import time
from django.db import connection
from django.db.models import Count, F
from django.http import JsonResponse

class BooksWithMultipleModelsView(APIView):
    def get(self, request):
        start_time = time.time()

        # Perform a complex query to join multiple models

        books = Book.objects.select_related('author', 'publisher').annotate(
            review_count=Count('review'),
            reviewss=F('review__text'),
            ratings=Cast(F('review__rating'), CharField())
        ).values(
            'id', 'title', 'author__name', 'publisher__name', 'genre__name',
            'review_count', 'reviewss', 'ratings'
        ).all()

        books_data = [
            {
                'title': book['title'],
                'author': book['author__name'],
                'publisher': book['publisher__name'],
                'genres': [genre for genre in book['genre__name']],
                 'reviews': [{'text': review, 'rating': rating} for review, rating in zip(book['reviewss'], book['ratings'])]

            }
            for book in books
        ]

        elapsed_time = time.time() - start_time

        # Log the executed database queries
        queries = connection.queries

        return JsonResponse({'books': books_data, 'elapsed_time': elapsed_time, 'queries': queries})

class BooksWithSerializersView(APIView):
    def get(self, request):
        start_time = time.time()

        # Retrieve all books
        books = Book.objects.all()

        # Serialize the data
        serializer = BookSerializer(books, many=True)
        books_data = serializer.data

        serializer_queries = connection.queries

        elapsed_time = time.time() - start_time

        return Response({'books': books_data, 'elapsed_time': elapsed_time,'queries': serializer_queries})