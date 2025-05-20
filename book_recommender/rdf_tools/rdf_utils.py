# rdf_tools/rdf_utils.py
import os
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from rdflib.namespace import XSD


BASE_IRI = "http://www.semanticweb.org/ursal/ontologies/2025/4/untitled-ontology-2#"
BK = Namespace(BASE_IRI)
RDF_DATA_FILE = "rdf_data/hw2seweb.rdf"


def load_rdf_graph():
    g = Graph()
    try:
        # dir exists?
        rdf_dir = os.path.dirname(RDF_DATA_FILE)
        if not os.path.exists(rdf_dir):
            os.makedirs(rdf_dir)
            print(f"Created directory: {rdf_dir}")

        if os.path.exists(RDF_DATA_FILE):
            g.parse(RDF_DATA_FILE, format="xml")
        else:
            print(f"RDF file not found at {RDF_DATA_FILE}, creating a new graph structure.")
            g.bind("bk", BK)
            g.bind("owl", Namespace("http://www.w3.org/2002/07/owl#"))
            g.add((URIRef(BASE_IRI.rstrip('#/')), RDF.type, URIRef("http://www.w3.org/2002/07/owl#Ontology")))
            save_rdf_graph(g)

    except Exception as e:
        print(f"Error loading or initializing RDF graph: {e}. Returning an empty graph with bindings.")
        g = Graph() # Ensure g is a Graph instance
        g.bind("bk", BK)
        g.bind("owl", Namespace("http://www.w3.org/2002/07/owl#"))
    return g

def save_rdf_graph(g):
    try:
        g.bind("bk", BK) # Ensure prefix is bound
        g.bind("owl", Namespace("http://www.w3.org/2002/07/owl#"))
        g.bind("rdf", RDF)
        g.bind("rdfs", Namespace("http://www.w3.org/2000/01/rdf-schema#"))
        g.bind("xsd", XSD)
        g.serialize(destination=RDF_DATA_FILE, format="pretty-xml")
        print(f"Saved RDF graph to {RDF_DATA_FILE}")
    except Exception as e:
        print(f"Error saving RDF graph: {e}")

def create_book_uri(title):
    slug = title.lower().replace(' ', '-').replace("'", "").replace(".", "").replace(":", "")
    return BK[slug]

# These expect the name as stored in your ontology, e.g., "Beginner", "Science Fiction"
def get_reading_level_uri_by_name(level_name_str):
    # Assumes level individuals are named like bk:BeginnerLevel, bk:IntermediateLevel
    # This is a simple mapping. A query would be more robust if names change.
    formatted_name = level_name_str.capitalize() + "Level"
    return BK[formatted_name]

def get_theme_uri_by_name(theme_name_str):
    # Assumes theme individuals are named like bk:FantasyTheme, bk:ScienceFictionTheme
    formatted_name = theme_name_str.replace(" ", "") + "Theme"
    return BK[formatted_name]