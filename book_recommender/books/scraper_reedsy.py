# books/scraper.py
import requests
from bs4 import BeautifulSoup
import xml.dom.minidom
import os
import random
import re
from django.conf import settings

def scrape_books():
    """
    Scrape books from a default URL and create an XML file with the scraped data. 
    If the XML directory does not exist, it will be automatically created.
    Use 'scrape_books.py' to scrape books. (books/management/commands/scrape_books.py)
    Command: python3 manage.py scrape_books
    
    Args:
        None
        
    Returns:
        dict    
    """
   
    themes = [
        "Fiction", "Science Fiction", "Fantasy", "Mystery", "Thriller", 
        "Romance", "Historical Fiction", "Non-Fiction", "Biography", 
        "Adventure", "Classic", "Horror", "Dystopian", 
        "Children's", "Memoir", "Philosophy", "Science", "Poetry"
    ]
    
    reading_levels = [
        "Beginner", 
        "Intermediate", 
        "Advanced"
    ]
    
    xml_dir = os.path.join(settings.BASE_DIR, 'xml_data')
    os.makedirs(xml_dir, exist_ok=True)
    
    books_file = os.path.join(xml_dir, 'books.xml')
    
    # header mimics  
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    
    url = "https://reedsy.com/discovery/blog/best-books-to-read-in-a-lifetime"
    response = requests.get(url, headers=headers)
    
    # html direct search patterns
    html_content = response.text
    
    # "<em>Book Title</em>"
    em_pattern = re.compile(r'<em>(.*?)</em>')
    matches = em_pattern.findall(html_content)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    """
    We will create a xml document and find book entries on the page.
    """
    scraped_titles = []
    
    if matches:
        for match in matches:
            title = match.strip()
            # hardcoded filters
            if (len(title) < 100 and len(title) > 3 and 
                not any(x in title.lower() for x in ['quiz', 'overwhelmed', 'recommendation', 'max'])):
                scraped_titles.append(title)
    else:
        for em in soup.find_all('em'):
            title = em.text.strip()
            if (title and len(title) < 100 and len(title) > 3 and 
                not any(x in title.lower() for x in ['quiz', 'overwhelmed', 'recommendation', 'max'])):
                scraped_titles.append(title)
                print(f"Found title from soup: {title}")
    
    doc = xml.dom.minidom.getDOMImplementation().createDocument(None, "books", None)
    root = doc.documentElement
    
    books_added = []
    for title in scraped_titles:
        if title not in books_added:  
            books_added.append(title)
            
            book = doc.createElement("book")
            
            title_elem = doc.createElement("title")
            title_text = doc.createTextNode(title)
            title_elem.appendChild(title_text)
            book.appendChild(title_elem)
            
            themes_elem = doc.createElement("themes")
            selected_themes = random.sample(themes, 2)
            
            for theme in selected_themes:
                theme_elem = doc.createElement("theme")
                theme_text = doc.createTextNode(theme)
                theme_elem.appendChild(theme_text)
                themes_elem.appendChild(theme_elem)
            
            book.appendChild(themes_elem)
            
            levels_elem = doc.createElement("reading_levels")
            selected_level = random.choice(reading_levels)
            level_elem = doc.createElement("level")
            level_text = doc.createTextNode(selected_level)
            level_elem.appendChild(level_text)
            levels_elem.appendChild(level_elem)
            
            book.appendChild(levels_elem)
            
            root.appendChild(book)
        
            if len(books_added) >= 20:
                break
    
    """
    Fallback to manually add books IF we did not scraped enough books.
    """
    
    # TODO: Implement manual book addition.
    
    """
    We will write to the xml books file after which we will create the users xml file where we will add one user.
    """
    
    with open(books_file, 'w', encoding='utf-8') as f:
        f.write(doc.toprettyxml(indent="  "))
    
    users_file = os.path.join(xml_dir, 'users.xml')
    
    doc = xml.dom.minidom.getDOMImplementation().createDocument(None, "users", None)
    root = doc.documentElement
    
    user = doc.createElement("user")
    
    name_elem = doc.createElement("name")
    name_text = doc.createTextNode("John")
    name_elem.appendChild(name_text)
    user.appendChild(name_elem)

    surname_elem = doc.createElement("surname")
    surname_text = doc.createTextNode("Doe")
    surname_elem.appendChild(surname_text)
    user.appendChild(surname_elem)

    reading_level_elem = doc.createElement("reading_level")
    reading_level_text = doc.createTextNode("Beginner")  
    reading_level_elem.appendChild(reading_level_text)
    user.appendChild(reading_level_elem)
    
    preferred_theme_elem = doc.createElement("preferred_theme")
    preferred_theme_text = doc.createTextNode("Fantasy")  
    preferred_theme_elem.appendChild(preferred_theme_text)
    user.appendChild(preferred_theme_elem)
    
    root.appendChild(user)
    
    with open(users_file, 'w', encoding='utf-8') as f:
        f.write(doc.toprettyxml(indent="  "))
    
    print(f"===== book count: {len(books_added)} =====")
    
    return {
        'books_count': len(books_added),
        'books_file': books_file,
        'users_file': users_file
    }