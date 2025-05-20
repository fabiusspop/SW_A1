from django.shortcuts import render
from .forms import RDFUploadForm 
from rdflib import Graph as RDFGraph
from rdflib.util import guess_format
from rdflib import URIRef, Literal, BNode
from pyvis.network import Network
from urllib.parse import urlparse 
import traceback # Keep for essential error logging if something unexpected happens
import tempfile 
import os 

def get_node_label(node):
    """Helper function to get a display label for an RDF node."""
    if isinstance(node, URIRef):
        s_node = str(node)
        # Try to get the part after '#' or the last part after '/'
        if '#' in s_node:
            return s_node.split('#')[-1] or s_node # Handle empty fragment
        else:
            return s_node.split('/')[-1] or s_node # Handle trailing slash or empty last segment
    elif isinstance(node, Literal):
        label_str = f'"{str(node)}"'
        if node.language:
            label_str += f"@{node.language}"
        elif node.datatype and str(node.datatype) != 'http://www.w3.org/2001/XMLSchema#string':
            label_str += f"^^<{str(node.datatype)}>" # Show full datatype URI
        return label_str
    elif isinstance(node, BNode):
        return f"_:{str(node)}" # Keep blank node prefix for clarity
    return str(node)

def upload_and_visualize_rdf(request):
    graph_html_content = None
    error_message = None
    form = RDFUploadForm() 

    if request.method == 'POST':
        form = RDFUploadForm(request.POST, request.FILES) 
        if form.is_valid():
            rdf_file = request.FILES['rdf_file']
            try:
                file_content_bytes = rdf_file.read()
                g = RDFGraph()
                # Default to 'xml' if guess_format returns None or for .owl files
                detected_format = guess_format(rdf_file.name)
                if detected_format is None or rdf_file.name.lower().endswith('.owl'):
                    detected_format = 'xml'
                
                g.parse(data=file_content_bytes, format=detected_format)

                if len(g) == 0: 
                    error_message = "Parsed RDF graph is empty or could not be parsed."
                else:
                    net = Network(height="750px", width="100%", directed=True, notebook=False, cdn_resources='remote')
                    net.set_options("""
                    var options = {
                      "nodes": {"font": {"size": 12}},
                      "edges": {
                        "arrows": {"to": {"enabled": true, "scaleFactor": 0.5}},
                        "font": {"size": 10, "align": "middle"},
                        "smooth": {"type": "continuous"}
                      },
                      "physics": {
                        "enabled": true, "solver": "barnesHut",
                        "barnesHut": {"gravitationalConstant": -8000, "springConstant": 0.001, "springLength": 200}
                      },
                      "interaction":{"hover":true, "tooltipDelay": 200}
                    }
                    """)
                    
                    nodes_added_set = set()
                    for s, p, o in g:
                        s_str, o_str = str(s), str(o)
                        if s_str not in nodes_added_set:
                            net.add_node(s_str, label=get_node_label(s), title=s_str, shape='ellipse')
                            nodes_added_set.add(s_str)
                        if o_str not in nodes_added_set:
                            net.add_node(o_str, label=get_node_label(o), title=o_str, 
                                         shape='box' if isinstance(o, Literal) else 'ellipse')
                            nodes_added_set.add(o_str)
                        net.add_edge(s_str, o_str, label=get_node_label(p), title=str(p))
                    
                    if net.nodes or net.edges: 
                        try:
                            graph_html_content = net.html # Attempt to get HTML via property

                            if not graph_html_content: # If empty, use the fallback
                                print("NOTE: net.html was empty, using temp file fallback for Pyvis.")
                                with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".html", encoding="utf-8", prefix="pyvis_graph_") as tmp_file:
                                    tmp_file_name = tmp_file.name
                                net.show(tmp_file_name, notebook=False) # Writes file, may try to open new tab
                                with open(tmp_file_name, "r", encoding="utf-8") as f_read:
                                    graph_html_content = f_read.read()
                                os.remove(tmp_file_name) # Clean up
                            
                            if not graph_html_content: # Still empty after all attempts
                                error_message = "Pyvis generated empty HTML content."
                        
                        except Exception as e_pyvis:
                            print(f"ERROR generating Pyvis HTML: {e_pyvis}\n{traceback.format_exc()}")
                            error_message = f"Error during Pyvis HTML generation: {str(e_pyvis)}"
                    else:
                        error_message = "Pyvis network object is empty (no nodes/edges added)."
            except Exception as e:
                print(f"ERROR processing RDF file: {e}\n{traceback.format_exc()}")
                error_message = f"Error processing RDF file: {str(e)}."
        else:
            error_message = "Invalid form submission. Please select a file."
            
    return render(request, 'rdf_tools/visualize_rdf.html', {
        'form': form, 
        'graph_html_content': graph_html_content,
        'error_message': error_message
    })










import io
import rdflib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from django.http import HttpResponse

def rdf_graph_view(request):
    g = rdflib.Graph()
    g.parse("test.rdf", format="xml")  # or load from request

    G = rdflib_to_networkx_multidigraph(g)
    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'r')

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color="skyblue", font_size=8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    # Save plot to a BytesIO buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')



# ex 2
import rdflib
import json
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from django.shortcuts import render

def rdf_graph_upload_view(request):
    if request.method == 'POST' and request.FILES.get('rdf_file'):
        rdf_file = request.FILES['rdf_file']
        rdf_format = request.POST.get('format', 'xml')

        def get_label(uri):
            if isinstance(uri, rdflib.term.URIRef):
                uri_str = str(uri)
                if '#' in uri_str:
                    return uri_str.split('#')[-1]
                elif '/' in uri_str:
                    return uri_str.rstrip('/').split('/')[-1]
                else:
                    return uri_str
            elif isinstance(uri, rdflib.term.BNode):
                return f"_:{str(uri)}"
            else:
                return str(uri)

        g = rdflib.Graph()
        g.parse(rdf_file, format=rdf_format)

        G = rdflib_to_networkx_multidigraph(g)


        nodes = []  
        edges = []

        for node in G.nodes():
            nodes.append({
                "id": str(node), 
                "label": get_label(node), 
            })

        for u, v, data in G.edges(data=True):
            predicate = data.get('predicate') or data.get('label') or ''
            label = get_label(predicate)

            edges.append({
                "from": str(u),
                "to": str(v),
                "label": label,
                "title": str(predicate)
                
            })

        return render(request, 'rdf_tools/visualize_rdf_good.html', {
            'nodes_json': json.dumps(nodes),
            'edges_json': json.dumps(edges),
        })


    return render(request, 'rdf_tools/rdf_upload.html')


# ex 4
from django.shortcuts import render, redirect
from django.urls import reverse
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from rdflib.namespace import XSD # Ensure XSD is imported

from .forms import BookRDFForm, ModifyReadingLevelForm
from .rdf_utils import (
    load_rdf_graph, save_rdf_graph, BK, 
    create_book_uri, get_reading_level_uri_by_name, get_theme_uri_by_name
)

def list_books_rdf(request):
    g = load_rdf_graph()
    books_list = []
    query = """
    SELECT ?book ?title WHERE {
        ?book rdf:type bk:Book .
        ?book bk:bookTitle ?title .
    } ORDER BY ?title
    """
    results = g.query(query, initNs={"bk": BK, "rdf": RDF}) 
    
    for row in results:
        book_uri_str = str(row.book)
        # Create a slug from the last part of the URI
        slug = book_uri_str.split('/')[-1].split('#')[-1]
        books_list.append({'title': str(row.title), 'slug': slug})
    return render(request, 'rdf_tools/list_books_rdf.html', {'books': books_list})


# ex 4 page for each book
def book_detail_rdf(request, book_slug):
    g = load_rdf_graph()
    book_subject_uri = BK[book_slug] # Reconstruct URI from slug

    details = {'uri': str(book_subject_uri), 'title': None, 'themes': [], 'reading_levels': []}
    
    # titlu
    title_results = list(g.objects(subject=book_subject_uri, predicate=BK.bookTitle))
    if not title_results:
        return render(request, 'rdf_tools/book_not_found.html', {'book_slug': book_slug})
    details['title'] = str(title_results[0])

    # theme
    for theme_uri in g.objects(subject=book_subject_uri, predicate=BK.hasBookTheme):
        theme_name = str(list(g.objects(subject=theme_uri, predicate=BK.themeName))[0])
        details['themes'].append(theme_name)
    
    # reading lvl
    for level_uri in g.objects(subject=book_subject_uri, predicate=BK.isSuitableForReadingLevel):
        level_name = str(list(g.objects(subject=level_uri, predicate=BK.levelName))[0])
        details['reading_levels'].append(level_name)
        
    return render(request, 'rdf_tools/book_detail_rdf.html', {'book': details})



# Task 3: Add a book
def add_book_rdf(request):
    if request.method == 'POST':
        form = BookRDFForm(request.POST)
        if form.is_valid():
            g = load_rdf_graph()
            title = form.cleaned_data['title']
            theme_name = form.cleaned_data['theme']
            level_name = form.cleaned_data['reading_level']

            new_book_s_uri = create_book_uri(title) # URI for the new book subject
            
            g.add((new_book_s_uri, RDF.type, BK.Book))
            g.add((new_book_s_uri, BK.bookTitle, Literal(title, datatype=XSD.string)))
            
            # Link to existing Theme and ReadingLevel individuals
            g.add((new_book_s_uri, BK.hasBookTheme, get_theme_uri_by_name(theme_name)))
            g.add((new_book_s_uri, BK.isSuitableForReadingLevel, get_reading_level_uri_by_name(level_name)))
            
            save_rdf_graph(g)
            return redirect(reverse('rdf_tools:list_books_rdf'))
    else:
        form = BookRDFForm()
    return render(request, 'rdf_tools/add_book_rdf.html', {'form': form})

# Task 3: Modify a book's reading level
def modify_book_reading_level(request, book_slug):
    g = load_rdf_graph()
    book_subject_uri = BK[book_slug]

    # Get current book title for display
    book_title = "Book" # Default
    title_res = list(g.objects(subject=book_subject_uri, predicate=BK.bookTitle))
    if title_res:
        book_title = str(title_res[0])
    else: # Book not found by slug
         return render(request, 'rdf_tools/book_not_found.html', {'book_slug': book_slug})


    if request.method == 'POST':
        form = ModifyReadingLevelForm(request.POST)
        if form.is_valid():
            new_level_name = form.cleaned_data['reading_level']
            new_level_o_uri = get_reading_level_uri_by_name(new_level_name)

            # Remove all old reading level(s) for this book
            g.remove((book_subject_uri, BK.isSuitableForReadingLevel, None))
            # Add the new one
            g.add((book_subject_uri, BK.isSuitableForReadingLevel, new_level_o_uri))
            
            save_rdf_graph(g)
            return redirect(reverse('rdf_tools:list_books_rdf'))
    else:
        # Pre-fill form (optional, for better UX)
        current_level_name = None
        current_level_uris = list(g.objects(subject=book_subject_uri, predicate=BK.isSuitableForReadingLevel))
        if current_level_uris:
            level_name_res = list(g.objects(subject=current_level_uris[0], predicate=BK.levelName))
            if level_name_res:
                current_level_name = str(level_name_res[0])
        form = ModifyReadingLevelForm(initial={'reading_level': current_level_name} if current_level_name else {})
        
    return render(request, 'rdf_tools/modify_book_reading_level.html', {
        'form': form, 
        'book_title': book_title,
        'book_slug': book_slug
    })