from django.core.management.base import BaseCommand
from books.xml_utils import get_book_by_title
import ollama


def format_book_for_context(book):
    title = book.get('title', 'Unknown Title')
    themes = ', '.join(book.get('themes', []))
    levels = ', '.join(book.get('reading_levels', []))
    return f"Title: {title}\nThemes: {themes}\nReading Levels: {levels}\n"


def build_prompt_template(prompt, context):
    return f"""You are a book recommender system. Based on the context provided, answer the question, and only the question. DO NOT add information that is not explicitly present in the context.


Context:
{context}

Question:
{prompt}

Answer:"""


def generate_response(prompt, model_name="llama3.2"):
    response = ollama.chat(
        model=model_name,
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant for book recommendations.'},
            {'role': 'user', 'content': prompt}
        ]
    )
    return response['message']['content'].strip()


class Command(BaseCommand):
    help = 'Run the RAG system to retrieve book themes using Ollama'

    def handle(self, *args, **kwargs):
        book = get_book_by_title("Animal Farm")
        if not book:
            self.stdout.write("Book not found.")
            return

        context = format_book_for_context(book)
        prompt = "What are the themes of the book?"
        full_prompt = build_prompt_template(prompt, context)

        self.stdout.write("Generating response from Ollama...")
        response = generate_response(full_prompt, model_name="llama3.2")

        self.stdout.write("\nResponse:\n")
        self.stdout.write(response)
