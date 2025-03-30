from django.db import models

# Create your models here.
class Theme(models.Model):
    name = models.CharField(max_length = 100, unique = True)
    
    def __str__(self):
        return self.name
    
class ReadingLevel(models.Model):
    name = models.CharField(max_length = 100, unique = True)
    
    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length = 200)
    themes = models.ManyToManyField(Theme, related_name = 'books', limit_choices_to = 2)
    reading_level = models.ManyToManyField(ReadingLevel, related_name = 'books')
    
    def __str__(self):
        return self.title
