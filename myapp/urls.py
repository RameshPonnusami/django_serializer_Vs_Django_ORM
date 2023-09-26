# urls.py
from django.urls import path
from .views import BooksWithMultipleModelsView, BooksWithSerializersView

urlpatterns = [
    path('books_with_multiple_models/', BooksWithMultipleModelsView.as_view(), name='books_with_multiple_models'),
    path('books_with_serializers/', BooksWithSerializersView.as_view(), name='books_with_serializers'),
]
