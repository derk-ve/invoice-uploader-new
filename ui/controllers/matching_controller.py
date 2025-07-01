"""
Controller for invoice matching business logic.
"""

import os
from pathlib import Path
from typing import List, Optional, Callable

from src.invoice_matching import PDFScanner, parse_mt940_file, do_bookkeeping
from src.invoice_matching.core.models import MatchingSummary
from src.utils.logging_setup import LoggingSetup


class MatchingController:
    """Controller for handling invoice matching business logic."""
    
    def __init__(self):
        """Initialize the matching controller."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        
        # Callbacks for progress updates
        self.on_step_start: Optional[Callable[[str], None]] = None
        self.on_transaction_loaded: Optional[Callable[[str, int, bool], None]] = None
        self.on_invoice_scanned: Optional[Callable[[str, Optional[str]], None]] = None
        self.on_summary_ready: Optional[Callable[[int, int], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def validate_files(self, mt940_files: List[str], pdf_files: List[str]) -> Optional[str]:
        """
        Validate selected files before processing.
        
        Args:
            mt940_files: List of MT940 file paths
            pdf_files: List of PDF file paths
            
        Returns:
            Error message if validation fails, None if valid
        """
        if not mt940_files:
            return "Please select MT940 transaction files first."
        
        if not pdf_files:
            return "Please select PDF invoice files first."
        
        # Check if files exist
        for file_path in mt940_files + pdf_files:
            if not Path(file_path).exists():
                return f"File not found: {Path(file_path).name}"
        
        return None
    
    def run_matching(self, mt940_files: List[str], pdf_files: List[str]) -> Optional[MatchingSummary]:
        """
        Run the complete invoice matching process.
        
        Args:
            mt940_files: List of MT940 file paths
            pdf_files: List of PDF file paths
            
        Returns:
            MatchingSummary if successful, None if error occurred
        """
        try:
            # Step 1: Load transactions
            if self.on_step_start:
                self.on_step_start("📄 Loading transactions from MT940 files...")
            
            transactions = self._load_transactions(mt940_files)
            if not transactions:
                if self.on_error:
                    self.on_error("No transactions loaded. Check your MT940 files.")
                return None
            
            # Step 2: Scan invoices
            if self.on_step_start:
                self.on_step_start("📁 Scanning PDF invoices...")
            
            invoices = self._scan_invoices(pdf_files)
            if not invoices:
                if self.on_error:
                    self.on_error("No invoices found. Check your PDF files.")
                return None
            
            # Summary stats
            if self.on_summary_ready:
                self.on_summary_ready(len(transactions), len(invoices))
            
            # Step 3: Run matching
            if self.on_step_start:
                self.on_step_start("🔍 Running matching algorithm...")
            
            summary = do_bookkeeping(transactions, invoices)
            
            self.logger.info(f"Matching complete: {len(summary.matched_pairs)} matches, "
                           f"{summary.match_rate:.1f}% match rate")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Matching error: {e}")
            if self.on_error:
                self.on_error(f"Error during matching: {e}")
            return None
    
    def _load_transactions(self, mt940_files: List[str]) -> List:
        """
        Load transactions from MT940 files.
        
        Args:
            mt940_files: List of MT940 file paths
            
        Returns:
            List of loaded transactions
        """
        transactions = []
        
        for mt940_file in mt940_files:
            try:
                file_transactions = parse_mt940_file(mt940_file)
                transactions.extend(file_transactions)
                
                # Report progress
                if self.on_transaction_loaded:
                    self.on_transaction_loaded(mt940_file, len(file_transactions), True)
                
                self.logger.debug(f"Loaded {len(file_transactions)} transactions from {Path(mt940_file).name}")
                
            except Exception as e:
                self.logger.error(f"Error loading {Path(mt940_file).name}: {e}")
                
                # Report error
                if self.on_transaction_loaded:
                    self.on_transaction_loaded(mt940_file, 0, False)
        
        self.logger.info(f"Total transactions loaded: {len(transactions)}")
        return transactions
    
    def _scan_invoices(self, pdf_files: List[str]) -> List:
        """
        Scan PDF files for invoice information.
        
        Args:
            pdf_files: List of PDF file paths
            
        Returns:
            List of scanned invoices
        """
        try:
            # Find common directory of selected files (same approach as demo.py)
            if len(pdf_files) == 1:
                common_dir = str(Path(pdf_files[0]).parent)
            else:
                common_dir = os.path.commonpath([str(Path(f).parent) for f in pdf_files])
            
            # Scan the directory once (same as demo.py)
            scanner = PDFScanner(common_dir)
            all_invoices_in_dir = scanner.scan()
            
            # Filter to only include selected files (compare filenames, not full paths)
            selected_filenames = [Path(f).name for f in pdf_files]
            all_invoices = [inv for inv in all_invoices_in_dir 
                           if Path(inv.file_path).name in selected_filenames]
            
            # Report progress for each selected file
            for pdf_file in pdf_files:
                filename = Path(pdf_file).name
                matching_invoices = [inv for inv in all_invoices 
                                   if Path(inv.file_path).name == filename]
                
                invoice_number = None
                if matching_invoices:
                    invoice_number = matching_invoices[0].invoice_number
                
                # Report progress
                if self.on_invoice_scanned:
                    self.on_invoice_scanned(pdf_file, invoice_number)
                
                if invoice_number:
                    self.logger.debug(f"Extracted invoice {invoice_number} from {filename}")
                else:
                    self.logger.warning(f"Could not extract invoice number from {filename}")
            
            self.logger.info(f"Total invoices found: {len(all_invoices)}")
            return all_invoices
            
        except Exception as e:
            self.logger.error(f"Error scanning invoices: {e}")
            if self.on_error:
                self.on_error(f"Error scanning invoices: {e}")
            return []
    
    # Callback setters
    def set_step_start_callback(self, callback: Callable[[str], None]):
        """Set callback for step start notifications."""
        self.on_step_start = callback
    
    def set_transaction_loaded_callback(self, callback: Callable[[str, int, bool], None]):
        """Set callback for transaction loading progress."""
        self.on_transaction_loaded = callback
    
    def set_invoice_scanned_callback(self, callback: Callable[[str, Optional[str]], None]):
        """Set callback for invoice scanning progress."""
        self.on_invoice_scanned = callback
    
    def set_summary_ready_callback(self, callback: Callable[[int, int], None]):
        """Set callback for summary statistics."""
        self.on_summary_ready = callback
    
    def set_error_callback(self, callback: Callable[[str], None]):
        """Set callback for error notifications."""
        self.on_error = callback