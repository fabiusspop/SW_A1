from django.shortcuts import render
from .xml_utils import get_books_from_xml

# Create your views here.

def book_list(request):
    books = get_books_from_xml()
    return render(request, 'books/book_list.html', {'books' : books})