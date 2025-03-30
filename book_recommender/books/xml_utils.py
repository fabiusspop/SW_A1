from lxml import etree
import os
from django.conf import settings

"""
    This module contains utility functions for XML files.
"""

def get_books_from_xml():
    xml_dir = os.path.join(settings.BASE_DIR, 'xml_data')
    books_file = os.path.join(xml_dir, 'books.xml')
    
    tree = etree.parse(books_file)
    books = []
    
    for book_elem in tree.xpath('//book'):
        title = book_elem.find('title').text 
        themes = [theme.text for theme in book_elem.findall('.//themes/theme')]
        reading_levels = [level.text for level in book_elem.findall('.//reading_levels/level')]
    
        books.append({
            'title' : title,
            'themes' : themes,
            "reading_levels" : reading_levels
        })

    return books