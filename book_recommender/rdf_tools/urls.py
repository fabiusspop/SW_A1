from django.urls import path
from . import views

app_name = 'rdf_tools' # Good practice for namespacing
urlpatterns = [
    path('visualize-rdf/', views.upload_and_visualize_rdf, name='visualize_rdf_upload'),
    path('tesint-graph/', views.rdf_graph_view,name="testgraph"),
    path('upload-graph/', views.rdf_graph_upload_view, name='rdf-upload-graph'),

]