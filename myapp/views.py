# views.py
import time
from django.db import connection
from django.db.models import Count, F
# from django.db.models.functions import Prefetch
from django.http import JsonResponse
from .models import Book, Author, Publisher, Genre, Review
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer
from django.db.models.functions import Cast
from django.db.models import  CharField

def books_with_multiple_models(request):
    start_time = time.time()

    # Perform a complex query to join multiple models
    books = Book.objects.select_related('author', 'publisher').prefetch_related('genre').all()

    # Accessing related data
    books_data = []
    for book in books:
        book_data = {
            'title': book.title,
            'author': book.author.name,
            'publisher': book.publisher.name,
            'genres': [genre.name for genre in book.genre.all()],
            'reviews': [{'text': review.text, 'rating': review.rating} for review in Review.objects.filter(book=book)]
        }
        books_data.append(book_data)

    elapsed_time = time.time() - start_time

    # Log the executed database queries
    queries = connection.queries

    return JsonResponse({'books': books_data, 'elapsed_time': elapsed_time, 'queries': queries,'total_queries_executed':len(queries)})





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
        )
        books_dict = {}
        for book in books:
            book_id = book['id']

            if book_id not in books_dict:
                # Create a new entry for the book
                books_dict[book_id] = {
                    'title': book['title'],
                    'author': book['author__name'],
                    'publisher': book['publisher__name'],
                    'genres': [genre for genre in book['genre__name']],
                    'reviews': []
                }
            books_dict[book_id]['reviews'].append({'text': book['reviewss'], 'rating': book['ratings']})

        # elapsed_time = time.time() - start_time

        elapsed_time = time.time() - start_time

        # Log the executed database queries
        queries = connection.queries

        return JsonResponse({'books': books_dict, 'total_books':len(books_dict),'elapsed_time': elapsed_time, 'queries': queries,
                             'total_queries_executed':len(queries)})



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

        return Response({'books': books_data,'total_books':len(books_data), 'elapsed_time': elapsed_time,'queries': serializer_queries,
                         'total_queries_executed':len(serializer_queries)})

