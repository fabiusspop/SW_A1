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

def add_book_to_xml(book_data):
    xml_dir = os.path.join(settings.BASE_DIR, 'xml_data')
    books_file = os.path.join(xml_dir, 'books.xml')
    
    tree = etree.parse(books_file)
    root = tree.getroot()
    
    book = etree.SubElement(root, 'book')
    title = etree.SubElement(book, 'title')
    title.text = book_data['title']
    
    themes = etree.SubElement(book, 'themes')
    
    for theme in book_data['themes']:
        theme_elem = etree.SubElement(themes, 'theme')
        theme_elem.text = theme
        
    reading_levels = etree.SubElement(book, 'reading_levels')
    
    for level in book_data['reading_levels']:
        level_elem = etree.SubElement(reading_levels, 'level')
        level_elem.text = level
        
    tree.write(books_file, pretty_print=True, xml_declaration=True, encoding='utf-8')
