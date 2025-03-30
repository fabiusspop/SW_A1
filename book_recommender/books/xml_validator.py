from lxml import etree
import os
from django.conf import settings

"""
    This module contains two functions for validating XML files against DTD and XSD.
    The functions are used in the management/commands/validate_xml.py to validate the XML files.
    Terminal command: python3 manage.py validate_xml
"""

def validate_with_dtd(xml_file, dtd_file):
    try:
        dtd = etree.DTD(open(dtd_file))
        xml_doc = etree.parse(xml_file)
        is_valid = dtd.validate(xml_doc)
        
        if is_valid:
            return True, "VALID XML - DTD"
        else:
            return False, f"INVALID XML CHECK DTD: {dtd.error_log}"
    except Exception as e:
        return False, f"sth went wrong: {str(e)}"

def validate_with_xsd(xml_file, xsd_file):
    try:
        xsd_doc = etree.parse(xsd_file)
        xsd = etree.XMLSchema(xsd_doc)
        xml_doc = etree.parse(xml_file)
        is_valid = xsd.validate(xml_doc)
        
        if is_valid:
            return True, "VALID XML - XSD"
        else:
            return False, f"INVALID XML CHECK XSD: {xsd.error_log}"
    except Exception as e:
        return False, f"sth went wrong: {str(e)}"