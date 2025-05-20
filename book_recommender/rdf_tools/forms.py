from django import forms

class RDFUploadForm(forms.Form):
    rdf_file = forms.FileField(label='Upload RDF/XML File')



READING_LEVEL_CHOICES = [
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced'),
]
THEME_CHOICES = [
    ('Science Fiction', 'Science Fiction'),
    ('Fantasy', 'Fantasy'),
    ('Mystery', 'Mystery'),
    ('Murder Novel', 'Murder Novel'),
    # Add other themes that exist as individuals with these exact names
]

class BookRDFForm(forms.Form):
    title = forms.CharField(label="Book Title", max_length=200)
    theme = forms.ChoiceField(label="Primary Theme", choices=THEME_CHOICES)
    reading_level = forms.ChoiceField(label="Suitable Reading Level", choices=READING_LEVEL_CHOICES)

class ModifyReadingLevelForm(forms.Form):
    reading_level = forms.ChoiceField(label="New Reading Level", choices=READING_LEVEL_CHOICES)