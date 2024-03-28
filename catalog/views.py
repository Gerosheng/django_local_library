from datetime import date
from urllib import request
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin

def index(request):
    num_books = Book.objects.all().count()

    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count()

    num_books_word = Book.objects.filter(title__icontains='word').count()

    num_genres_word = Genre.objects.filter(name__icontains='word').count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_books_word': num_books_word,
        'num_genres_word': num_genres_word,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book

    paginate_by = 10

    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    
    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['some_data'] = 'This is just some data'

        return context

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_genres = set()
        all_languages = set()

        books = Book.objects.filter(author=self.object).prefetch_related('genre', 'language')

        for book in books:
            for genre in book.genre.all():
                all_genres.add(genre.name)

            all_languages.add(book.language.name)

        books_with_status_counts = books.annotate(
            total_instances=Count('bookinstance'),
            available=Count('bookinstance', filter=Q(bookinstance__status='a')),
            on_loan=Count('bookinstance', filter=Q(bookinstance__status='o')),
            reserved=Count('bookinstance', filter=Q(bookinstance__status='r')),
            maintenance=Count('bookinstance', filter=Q(bookinstance__status='m')),
            overdue=Count('bookinstance', filter=Q(bookinstance__status='o', bookinstance__due_back__lt=date.today())),
        )
        
        context['genres'] = list(all_genres)
        context['languages'] = list(all_languages)
        context['books_with_status_counts'] = books_with_status_counts

        return context


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance

    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )