from django import forms

class RDFUploadForm(forms.Form):
    rdf_file = forms.FileField(label='Upload RDF/XML File')