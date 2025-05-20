from django.urls import path
from . import views

app_name = 'rdf_tools' # Good practice for namespacing
urlpatterns = [
    path('visualize-rdf/', views.upload_and_visualize_rdf, name='visualize_rdf_upload'),
    path('tesint-graph/', views.rdf_graph_view,name="testgraph"),
    path('upload-graph/', views.rdf_graph_upload_view, name='rdf-upload-graph'),

    # ex 3
    path('books/add-new/', views.add_book_rdf, name='add_book_rdf'),
    path('books/modify-level/<slug:book_slug>/', views.modify_book_reading_level, name='modify_book_reading_level'),


    # ex 4
    path('books/', views.list_books_rdf, name='list_books_rdf'),
    path('books/<slug:book_slug>/', views.book_detail_rdf, name='book_detail_rdf'),

  
]