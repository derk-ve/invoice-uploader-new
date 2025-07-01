"""
Simple PDF scanner for filename-based invoice extraction.
"""

import os
import re
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .models import Invoice
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.logging_setup import LoggingSetup


class PDFScanner:
    """
    Simple scanner to find PDF files and extract invoice numbers from filenames.
    """
    
    def __init__(self, scan_directory: str):
        """
        Initialize PDF scanner.
        
        Args:
            scan_directory: Directory path to scan for PDF files
        """
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.scan_directory = Path(scan_directory)
        
        # Simple filename patterns for invoice number extraction
        self.patterns = [
            r'SIP\d{7,9}',   
        ]
        
        self.logger.debug(f"Initialized PDF scanner for directory: {scan_directory}")
    
    def scan(self) -> List[Invoice]:
        """
        Scan directory for PDF files and extract invoice information.
        
        Returns:
            List of Invoice objects created from PDF filenames
            
        Raises:
            FileNotFoundError: If scan directory doesn't exist
        """
        self.logger.info(f"Starting PDF scan in directory: {self.scan_directory}")
        
        if not self.scan_directory.exists():
            self.logger.error(f"Scan directory does not exist: {self.scan_directory}")
            raise FileNotFoundError(f"Scan directory does not exist: {self.scan_directory}")
        
        if not self.scan_directory.is_dir():
            self.logger.error(f"Scan path is not a directory: {self.scan_directory}")
            raise ValueError(f"Scan path is not a directory: {self.scan_directory}")
        
        invoices = []
        
        # Find all PDF files in directory
        pdf_files = list(self.scan_directory.glob("*.pdf"))
        pdf_files.extend(list(self.scan_directory.glob("*.PDF")))  # Case insensitive
        
        self.logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            invoice_number = self._extract_invoice_number(pdf_file.name)
            
            if invoice_number:
                invoice = Invoice(
                    invoice_number=invoice_number,
                    file_path=str(pdf_file.absolute()),
                    description=f"PDF Invoice: {pdf_file.name}"
                )
                invoices.append(invoice)
                self.logger.debug(f"Extracted invoice {invoice_number} from {pdf_file.name}")
            else:
                self.logger.warning(f"Could not extract invoice number from {pdf_file.name}")
        
        self.logger.info(f"PDF scan complete: {len(invoices)} invoices extracted from {len(pdf_files)} files")
        return invoices
    
    def _extract_invoice_number(self, filename: str) -> Optional[str]:
        """
        Extract invoice number from PDF filename using simple patterns.
        
        Args:
            filename: PDF filename to parse
            
        Returns:
            Extracted invoice number or None if not found
        """
        # Remove .pdf extension for easier matching
        name_without_ext = filename.lower().replace('.pdf', '')
        original_name = filename.replace('.pdf', '').replace('.PDF', '')
        
        # Try each pattern
        for pattern in self.patterns:
            # Try case-insensitive match first
            self.logger.debug(f"Trying pattern: {pattern} on {name_without_ext}")
            match = re.search(pattern.lower(), name_without_ext)
            if match:
                # Return the original case version
                original_match = re.search(pattern, original_name, re.IGNORECASE)
                if original_match:
                    return original_match.group(1)
        
        return None
    
    def add_pattern(self, pattern: str):
        """
        Add a custom regex pattern for invoice number extraction.
        
        Args:
            pattern: Regex pattern with one capture group for the invoice number
        """
        if pattern not in self.patterns:
            self.patterns.append(pattern)
            self.logger.debug(f"Added custom pattern: {pattern}")
    
    def get_supported_patterns(self) -> List[str]:
        """
        Get list of currently supported filename patterns.
        
        Returns:
            List of regex patterns used for extraction
        """
        return self.patterns.copy()


def scan_pdfs_for_invoices(directory: str) -> List[Invoice]:
    """
    Convenience function to scan a directory for PDF invoices.
    
    Args:
        directory: Directory path to scan
        
    Returns:
        List of Invoice objects extracted from PDF filenames
    """
    scanner = PDFScanner(directory)
    return scanner.scan()