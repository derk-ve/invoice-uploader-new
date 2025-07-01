"""
Simple unit tests for invoice matching functionality.
"""

import unittest
import tempfile
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from ..core.models import Transaction, Invoice
from ..core.matcher import do_bookkeeping
from ..core.pdf_scanner import PDFScanner


class TestBasicMatching(unittest.TestCase):
    """Test basic invoice matching functionality."""
    
    def test_simple_filename_match(self):
        """Test basic filename-based matching."""
        transactions = [
            Transaction(
                amount=Decimal('-125.50'),
                description="Payment for invoice INV-2024-001",
                date=datetime(2024, 1, 15),
                reference="TXN001"
            )
        ]
        
        invoices = [
            Invoice(
                invoice_number="INV-2024-001",
                file_path="/path/to/INV-2024-001.pdf"
            )
        ]
        
        summary = do_bookkeeping(transactions, invoices)
        
        self.assertEqual(len(summary.matched_pairs), 1)
        self.assertEqual(len(summary.unmatched_transactions), 0)
        self.assertEqual(summary.matched_pairs[0].invoice.invoice_number, "INV-2024-001")
    
    def test_no_match(self):
        """Test when no matches are found."""
        transactions = [
            Transaction(
                amount=Decimal('-25.00'),
                description="Coffee supplies - no invoice number",
                date=datetime(2024, 1, 18),
                reference="TXN003"
            )
        ]
        
        invoices = [
            Invoice(
                invoice_number="INV-2024-001",
                file_path="/path/to/INV-2024-001.pdf"
            )
        ]
        
        summary = do_bookkeeping(transactions, invoices)
        
        self.assertEqual(len(summary.matched_pairs), 0)
        self.assertEqual(len(summary.unmatched_transactions), 1)


class TestPDFScanner(unittest.TestCase):
    """Test PDF scanning functionality."""
    
    def setUp(self):
        """Create temporary directory with test PDF files."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test PDF files
        test_files = ["INV-2024-001.pdf", "Invoice_123.pdf", "ABC-456.pdf"]
        for filename in test_files:
            (Path(self.temp_dir) / filename).touch()
    
    def tearDown(self):
        """Clean up test directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_scan_finds_pdfs(self):
        """Test that scanner finds PDF files."""
        scanner = PDFScanner(self.temp_dir)
        invoices = scanner.scan()
        
        self.assertGreater(len(invoices), 0)
        
        # Check that we get invoice numbers
        invoice_numbers = [inv.invoice_number for inv in invoices]
        self.assertIn("INV-2024-001", invoice_numbers)
        self.assertIn("123", invoice_numbers)
        self.assertIn("ABC-456", invoice_numbers)
    
    def test_empty_directory(self):
        """Test scanning empty directory."""
        empty_dir = tempfile.mkdtemp()
        try:
            scanner = PDFScanner(empty_dir)
            invoices = scanner.scan()
            self.assertEqual(len(invoices), 0)
        finally:
            os.rmdir(empty_dir)


class TestEndToEnd(unittest.TestCase):
    """Test complete workflow."""
    
    def test_complete_workflow(self):
        """Test scanning PDFs and matching with transactions."""
        # Create temp directory with PDFs
        temp_dir = tempfile.mkdtemp()
        try:
            # Create PDF files
            (Path(temp_dir) / "INV-2024-001.pdf").touch()
            (Path(temp_dir) / "INV-2024-002.pdf").touch()
            
            # Scan for invoices
            scanner = PDFScanner(temp_dir)
            invoices = scanner.scan()
            
            # Create matching transactions
            transactions = [
                Transaction(
                    amount=Decimal('-100.00'),
                    description="Payment INV-2024-001",
                    date=datetime(2024, 1, 15),
                    reference="TXN001"
                ),
                Transaction(
                    amount=Decimal('-50.00'),
                    description="Payment INV-2024-002", 
                    date=datetime(2024, 1, 16),
                    reference="TXN002"
                )
            ]
            
            # Match them
            summary = do_bookkeeping(transactions, invoices)
            
            # Verify results
            self.assertEqual(len(summary.matched_pairs), 2)
            self.assertEqual(len(summary.unmatched_transactions), 0)
            
            # Check file paths are included
            for match in summary.matched_pairs:
                self.assertTrue(match.invoice.file_path.endswith('.pdf'))
        
        finally:
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()