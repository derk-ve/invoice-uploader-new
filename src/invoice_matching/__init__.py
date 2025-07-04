"""
Invoice matching system for SnelStart automation.

This module provides functionality to match MT940 bank transactions
with PDF invoices based on filename and description criteria.
"""

from .core.matcher import InvoiceMatcher, do_bookkeeping
from .core.models import Transaction, Invoice, MatchResult, MatchingSummary
from .core.pdf_scanner import PDFScanner, scan_pdfs_for_invoices
from .core.mt940_parser import MT940Parser, parse_mt940_file
from .core.mt940_generator import MT940Generator
from .core.upload_data_generator import UploadDataGenerator, UploadDataPackage

__all__ = [
    'InvoiceMatcher',
    'do_bookkeeping',
    'Transaction',
    'Invoice', 
    'MatchResult',
    'MatchingSummary',
    'PDFScanner',
    'scan_pdfs_for_invoices',
    'MT940Parser',
    'parse_mt940_file',
    'MT940Generator',
    'UploadDataGenerator',
    'UploadDataPackage'
]

__version__ = "0.1.0"