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

    # pretty printer to format the output
    xml_string = etree.tostring(root, encoding='utf-8')
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_string, parser)
    
    with open(users_file, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(etree.tostring(root, encoding='utf-8', pretty_print=True))
        
        
def get_first_user():
    xml_dir = os.path.join(settings.BASE_DIR, 'xml_data')
    users_file = os.path.join(xml_dir, 'users.xml')
    
    tree = etree.parse(users_file)
    
    user_element = tree.xpath('//user[1]')
    
    if not user_element:
        return None
    
    user = user_element[0]
    
    name = user.find('name').text
    surname = user.find('surname').text
    reading_level = user.find('reading_level').text
    preferred_theme = user.find('preferred_theme').text
    
    return {
        'name' : name,
        'surname' : surname,
        'reading_level' : reading_level,
        'preferred_theme' : preferred_theme
    }


def get_books_by_reading_level(reading_level):
    xml_dir = os.path.join(settings.BASE_DIR, 'xml_data')
    books_file = os.path.join(xml_dir, 'books.xml')
    
    tree = etree.parse(books_file)
    
    
    # find books where any level element contains the exact reading level
    xpath_query = f"//book[reading_levels/level = '{reading_level}']"
    book_elements = tree.xpath(xpath_query)
    
    books = []
    for book_elem in book_elements:
        title = book_elem.find('title').text
        themes = [theme.text for theme in book_elem.findall('.//themes/theme')]
        reading_levels = [level.text for level in book_elem.findall('.//reading_levels/level')]
        
        books.append({
            'title': title,
            'themes': themes,
            'reading_levels': reading_levels
        })
    
    return books

def get_books_by_reading_level_and_theme(reading_level, theme):
    xml_dir = os.path.join(settings.BASE_DIR, 'xml_data')
    books_file = os.path.join(xml_dir, 'books.xml')
    
    tree = etree.parse(books_file)
    
    xpath_query = f"//book[reading_levels/level = '{reading_level}' and themes/theme = '{theme}']"
    book_elements = tree.xpath(xpath_query)
    
    books = []
    for book_elem in book_elements:
        title = book_elem.find('title').text
        themes = [theme.text for theme in book_elem.findall('.//themes/theme')]
        reading_levels = [level.text for level in book_elem.findall('.//reading_levels/level')]
        
        books.append({
            'title': title,
            'themes': themes,
            'reading_levels': reading_levels
        })
    
    return books

def get_book_by_title(title):
    xml_dir = os.path.join(settings.BASE_DIR, 'xml_data')
    books_file = os.path.join(xml_dir, 'books.xml')
    
    tree = etree.parse(books_file)
    
    xpath_query = f"//book[title = '{title}']"
    book_elements = tree.xpath(xpath_query)
    
    if not book_elements:
        return None
    
    book_elem = book_elements[0]
    
    title = book_elem.find('title').text
    themes = [theme.text for theme in book_elem.findall('.//themes/theme')]
    reading_levels = [level.text for level in book_elem.findall('.//reading_levels/level')]
    
    return {
        'title': title,
        'themes': themes,
        'reading_levels': reading_levels
    }