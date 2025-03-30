from django.shortcuts import render, redirect
from django import forms

from .xml_utils import *

# Create your views here.

def book_list(request):
    books = get_books_from_xml()
    return render(request, 'books/book_list.html', {'books' : books})

class BookForm(forms.Form):
    
    title = forms.CharField(max_length=200, required=True)
    
    theme1 = forms.CharField(max_length=100, required=True, label="Theme 1")
    theme2 = forms.CharField(max_length=100, required=True, label="Theme 2")
    
    level1 = forms.CharField(max_length=100, required=True, label="Reading Level 1")
    level2 = forms.CharField(max_length=100, required=True, label="Reading Level 2")
    level3 = forms.CharField(max_length=100, required=True, label="Reading Level 3")
    
    def clean(self):
        cleaned_data = super().clean()
        
        theme1 = cleaned_data.get('theme1')
        theme2 = cleaned_data.get('theme2')
        
        if theme1 == theme2:
            raise forms.ValidationError("Themes cannot be the same.")
        
        return cleaned_data
    
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book_data = {
                'title' : form.cleaned_data['title'],
                'themes' : [form.cleaned_data['theme1'], form.cleaned_data['theme2']],
                'reading_levels' : [
                    form.cleaned_data['level1'],
                    form.cleaned_data['level2'],
                    form.cleaned_data['level3']
                ]
            }
            
            add_book_to_xml(book_data)
            
            return redirect('book_list')
    else:
        form = BookForm()
        
    return render(request, 'books/add_book.html', {'form' : form})

class UserForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    surname = forms.CharField(max_length=100, required=True)
    reading_level = forms.ChoiceField(
        choices = [('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')],
        required=True
    )
    preferred_theme = forms.CharField(max_length=100, required=True)
    
def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        
        if form.is_valid():
            user_data = {
                'name' : form.cleaned_data['name'],
                'surname' : form.cleaned_data['surname'],
                'reading_level' : form.cleaned_data['reading_level'],
                'preferred_theme' : form.cleaned_data['preferred_theme']
            }
            
            add_user_to_xml(user_data)
            
            return redirect('book_list')
    else:
        form = UserForm()
        
    return render(request, 'books/add_user.html', {'form' : form})

def recommend_by_level(request):
    user = get_first_user()
    
    if not user:
        return render(request, 'books/no_user.html')
    
    reading_level = user['reading_level']
    
    recommended_books = get_books_by_reading_level(reading_level)
    
    
    return render(request, 'books/recommend_by_level.html', {
        'user': user,
        'books': recommended_books
    })

def recommend_by_level_and_theme(request):
    user = get_first_user()

    if not user:
        return render(request, 'books/no_user.html')
    
    reading_level = user['reading_level']
    preferred_theme = user['preferred_theme']

    recommended_books = get_books_by_reading_level_and_theme(reading_level, preferred_theme)

    return render(request, 'books/recommend_by_level_and_theme.html', {
        'user': user,
        'books': recommended_books
    })

def display_book_details(request, title):
    book = get_book_by_title(title)
    
    if not book:
        return render(request, 'books/no_book.html')
    
    return render(request, 'books/book_details.html', {'book': book})