from django.shortcuts import render, redirect
from django import forms
from .xml_utils import get_books_from_xml, add_book_to_xml

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
