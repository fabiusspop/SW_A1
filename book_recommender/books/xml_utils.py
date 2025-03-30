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


def add_user_to_xml(user_data):
    xml_dir = os.path.join(settings.BASE_DIR, 'xml_data')
    users_file = os.path.join(xml_dir, 'users.xml')
    
    tree = etree.parse(users_file)
    root = tree.getroot()
    
    user = etree.SubElement(root, 'user')
    
    name = etree.SubElement(user, 'name')
    name.text = user_data['name']
    
    surname = etree.SubElement(user, 'surname')
    surname.text = user_data['surname']
    
    reading_level = etree.SubElement(user, 'reading_level')
    reading_level.text = user_data['reading_level']
    
    preferred_theme = etree.SubElement(user, 'preferred_theme')
    preferred_theme.text = user_data['preferred_theme']
    
    # this prints without identation 
    # tree.write(users_file, pretty_print=True, xml_declaration=True, encoding='utf-8')

    # pretty printer to format the output
    xml_string = etree.tostring(root, encoding='utf-8')
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_string, parser)
    
    with open(users_file, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(etree.tostring(root, encoding='utf-8', pretty_print=True))