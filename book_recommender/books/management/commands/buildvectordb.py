from django.core.management.base import BaseCommand
from books.vector_db import build_vector_db

class Command(BaseCommand):
    help = 'Build the vector database for the chatbot (RAG)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Building vector database...')
        build_vector_db()
        self.stdout.write(self.style.SUCCESS('Vector database built successfully.')) 