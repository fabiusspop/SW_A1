from django.shortcuts import render, redirect
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import ollama
from .vector_db import query_vector_db, search_by_theme_and_author
import json

from .xml_utils import *

# Create your views here.

class InputUser(forms.Form):
    name = forms.CharField(max_length=100, required=True)

def book_list(request):
    

    if request.method == 'POST':
        form = InputUser(request.POST)
        if form.is_valid():
            user_data = {
                'name' : form.cleaned_data['name']
            }
            
            books, user = get_books_from_xml_by_user(user_data['name'])
            if not user:
                return render(request, 'books/no_user.html')
            
            form = InputUser() 
            return render(request, 'books/book_list.html', {'books' : books, 'user' : user, 'form' : form})
    else:  
        form = InputUser() 
        books, user = get_books_from_xml()
        return render(request, 'books/book_list.html', {'books' : books, 'user' : user, 'form' : form})

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

@csrf_exempt
def chat_rag(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        # Book search by theme and author
        if "author" in user_message.lower() and "theme" in user_message.lower():
            # naive extraction
            import re
            author_match = re.search(r"author ([\w\s]+)", user_message, re.IGNORECASE)
            theme_match = re.search(r"theme ([\w\s]+)", user_message, re.IGNORECASE)
            author = author_match.group(1).strip() if author_match else ""
            theme = theme_match.group(1).strip() if theme_match else ""
            books = search_by_theme_and_author(theme, author)
            if books:
                titles = ", ".join([b['title'] for b in books])
                return JsonResponse({"response": f"Books by {author} with theme {theme}: {titles}"})
            else:
                return JsonResponse({"response": "No books found for that author and theme."})
        # Otherwise, do RAG
        context_books = query_vector_db(user_message)
        # Include author in the context
        context = "\n".join([f"Title: {b['title']}, Author: {b.get('author', '')}, Themes: {', '.join(b.get('themes', []))}, Levels: {', '.join(b.get('reading_levels', []))}" for b in context_books])
        prompt = f"Context:\n{context}\n\nQuestion: {user_message}\n\nAnswer based strictly on the provided context:"
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "system", "content": "You are a book assistant. You will ONLY answer questions based on the provided context. If the information is not in the context, say you don't know."},
                      {"role": "user", "content": prompt}]
        )
        answer = response['message']['content'].strip()
        return JsonResponse({"response": answer})

@csrf_exempt
def chat_starters(request):
    # Example: context-aware starters
    context = request.GET.get('context', 'list')
    book_title = request.GET.get('book_title', None)
    starters = []
    if context == 'book' and book_title:
        starters = [
            f"What is the genre of {book_title}?",
            f"Who is the author of {book_title}?",
            f"Can you recommend similar books to {book_title}?"
        ]
    else:
        starters = [
            "What is a book that I am most likely to enjoy from this list?",
            "Which book matches my reading level?",
            "Recommend a book based on my favorite theme."
        ]
    return JsonResponse({"starters": starters})

def chatbot_page(request):
    return render(request, 'books/chatbot_page.html')