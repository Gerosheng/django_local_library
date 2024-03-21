from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre

def index(request):
    num_books = Book.objects.all().count()

    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count()

    num_books_word = Book.objects.filter(title__icontains='word').count()

    num_genres_word = Genre.objects.filter(name__icontains='word').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_books_word': num_books_word,
        'num_genres_word': num_genres_word,
    }

    return render(request, 'index.html', context=context)

# Create your views here.
