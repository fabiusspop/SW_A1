from django.core.management.base import BaseCommand
from books.scraper_reedsy import scrape_books


class Command(BaseCommand):
    help = "Scrape book from the provided url and save to xml files"
    
    def handle(self, *args, **options):
        result = scrape_books()
        
        self.stdout.write(self.style.SUCCESS(f"Successfully scraped {result['books_count']} books"))
        self.stdout.write(f"Books saved to {result['books_file']}")
        self.stdout.write(f"Users saved to {result['users_file']}")
