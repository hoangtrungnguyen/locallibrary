import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View, generic
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from catalog.models import Genre, Book, BookInstance, Author
from .form import RenewBookForm, RenewBookModelForm,AuthorCreateForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView


def index(request):
    """View function for home page of site."""

    # Generate book's and num of book's instance
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books with status 'a'
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # the 'all()' is implied by default
    num_authors = Author.objects.count()

    num_genre = Genre.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre': num_genre,
        'num_visits': num_visits
    }

    return render(request, 'index.html', context=context)


class AuthorListView(generic.ListView):
    model = Author
    queryset = Author.objects.all()
    context_object_name = 'author_list'
    template_name = 'author/author_list.html'
    paginate_by = 20


class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'
    queryset = Book.objects.all()
    template_name = 'books/book_list.html'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context["name"] = "Local Library"
        return context


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'

    def get_object(self, queryset=None):
        return super().get_object(queryset)


class AuthorDetailView(generic.DetailView):
    model = Author

    def get_object(self, queryset=None):
        return super().get_object(queryset)


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(
            status__exact='o').order_by('due_back')


class BorrowedBookListview(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = BookInstance

    template_name = "books/bookinstance_list_borrowed_all.html"
    paginate_by = 20
    permission_required = ('catalog.can_mark_returned',)
    permission_denied_message = "You do not have permission"
    # redirect_field_name =
    raise_exception = True

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

    def get_permission_required(self):
        permissions = super().get_permission_required()
        return permissions


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    # form = RenewBookForm()
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # process the data in form.cleaned_data as required
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()
            # redirect to a new Url
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'book_instance': book_instance,
        'form': form
    }
    return render(request, 'catalog/book_renew_librarian.html', context)


# Author Form
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    form_class = AuthorCreateForm
    success_url = '/catalog/authors'
    permission_required = ('catalog.can_mark_returned',)
    # template_name_suffix = 'author'
    initial = {"date_of_death": "12-28-1988"}
    template_name = 'author/author_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('catalog.can_mark_returned',)
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('catalog.can_mark_returned',)
    model = Author
    template_name = 'author/author_confirm_delete.html'
    success_url = reverse_lazy('authors')


# Book's form
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    template_name = 'books/book_form.html'
    permission_required = ('catalog.can_mark_returned',)
    fields = "__all__"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('catalog.can_mark_returned',)
    model = Book
    fields = "__all__"
    template_name = "books/book_form.html"


class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('catalog.can_mark_returned',)
    model = Book
    template_name = "books/books_confirm_delete.html"
    success_url = reverse_lazy('books')
