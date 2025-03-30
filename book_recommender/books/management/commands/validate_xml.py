from django.core.management.base import BaseCommand
import os
from django.conf import settings
from books.xml_validator import validate_with_dtd, validate_with_xsd

class Command(BaseCommand):
    help = "Validate XML files against DTD and XSD"
    
    def handle(self, *args, **options):
        xml_dir = os.path.join(settings.BASE_DIR, 'xml_data')
        books_xml = os.path.join(xml_dir, 'books.xml')
        users_xml = os.path.join(xml_dir, 'users.xml')
        dtd_file = os.path.join(xml_dir, 'books.dtd')
        xsd_file = os.path.join(xml_dir, 'books.xsd')
        
        valid_dtd, msg_dtd = validate_with_dtd(books_xml, dtd_file)
        self.stdout.write(f"Books XML - DTD: {msg_dtd}")
        
        valid_dtd_users, msg_dtd_users = validate_with_dtd(users_xml, dtd_file)
        self.stdout.write(f"Users XML - DTD: {msg_dtd_users}")
        
        valid_xsd, msg_xsd = validate_with_xsd(books_xml, xsd_file)
        self.stdout.write(f"Books XML - XSD: {msg_xsd}")
        
        valid_xsd_users, msg_xsd_users = validate_with_xsd(users_xml, xsd_file)
        self.stdout.write(f"Users XML - XSD: {msg_xsd_users}")
        
        if valid_dtd and valid_dtd_users and valid_xsd and valid_xsd_users:
            self.stdout.write(self.style.SUCCESS("VALID XML FILES!"))
        else:
            self.stdout.write(self.style.ERROR("INVALID XML FILES!"))