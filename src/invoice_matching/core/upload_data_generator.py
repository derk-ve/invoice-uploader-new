"""
Upload data generator for preparing SnelStart upload packages.
"""

import os
import shutil
import tempfile
import signal
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path

from .models import MatchResult, MatchingSummary
from .mt940_generator import MT940Generator
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.logging_setup import LoggingSetup


@dataclass
class UploadDataPackage:
    """
    Container for all data needed for SnelStart upload.
    
    Attributes:
        mt940_file_path: Path to generated MT940 file with matched transactions
        pdf_files: Dictionary mapping invoice numbers to PDF file paths
        transaction_mapping: Dictionary mapping transaction references to invoice numbers
        total_matches: Total number of matched transaction-invoice pairs
        temp_directory: Temporary directory containing all files (for cleanup)
    """
    mt940_file_path: str
    pdf_files: Dict[str, str]  # {invoice_number: pdf_path}
    transaction_mapping: Dict[str, str]  # {transaction_reference: invoice_number}
    total_matches: int
    temp_directory: str


class UploadDataGenerator:
    """Generates complete upload packages for SnelStart from matching results."""
    
    def __init__(self, progress_callback=None):
        """
        Initialize the upload data generator.
        
        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.mt940_generator = MT940Generator()
        self.progress_callback = progress_callback
        
    def prepare_upload_data(self, summary: MatchingSummary, temp_base_dir: Optional[str] = None) -> UploadDataPackage:
        """
        Prepare complete upload package from matching summary.
        
        Args:
            summary: Matching results containing matched pairs
            temp_base_dir: Base directory for temporary files (optional)
            
        Returns:
            UploadDataPackage with all files ready for upload
            
        Raises:
            ValueError: If no matched pairs found
            IOError: If file operations fail
        """
        if not summary.matched_pairs:
            raise ValueError("No matched pairs found in summary")
            
        self.logger.info(f"Preparing upload data for {len(summary.matched_pairs)} matched pairs")
        
        # Create temporary directory for upload files
        if temp_base_dir:
            os.makedirs(temp_base_dir, exist_ok=True)
            temp_dir = tempfile.mkdtemp(dir=temp_base_dir, prefix="snelstart_upload_")
        else:
            temp_dir = tempfile.mkdtemp(prefix="snelstart_upload_")
            
        self.logger.debug(f"Created temporary upload directory: {temp_dir}")
        
        try:
            # 1. Generate MT940 file from matched transactions
            self._report_progress("📄 Generating MT940 file...")
            mt940_file_path = self._generate_mt940_file(summary.matched_pairs, temp_dir)
            
            # 2. Copy matched PDF files to upload directory
            self._report_progress(f"📁 Copying {len(summary.matched_pairs)} PDF files...")
            pdf_files = self._copy_matched_pdfs(summary.matched_pairs, temp_dir)
            
            # 3. Create transaction-to-invoice mapping
            self._report_progress("🔗 Creating transaction mapping...")
            transaction_mapping = self._create_transaction_mapping(summary.matched_pairs)
            
            # 4. Create upload package
            upload_package = UploadDataPackage(
                mt940_file_path=mt940_file_path,
                pdf_files=pdf_files,
                transaction_mapping=transaction_mapping,
                total_matches=len(summary.matched_pairs),
                temp_directory=temp_dir
            )
            
            self.logger.info(f"Upload package prepared successfully in {temp_dir}")
            self.logger.info(f"Package contains: 1 MT940 file, {len(pdf_files)} PDF files")
            
            return upload_package
            
        except Exception as e:
            # Clean up on error
            self._cleanup_temp_directory(temp_dir)
            self.logger.error(f"Failed to prepare upload data: {e}")
            raise
            
    def _generate_mt940_file(self, matched_pairs: List[MatchResult], temp_dir: str) -> str:
        """
        Generate MT940 file containing only matched transactions.
        
        Args:
            matched_pairs: List of matched transaction-invoice pairs
            temp_dir: Directory to save the MT940 file
            
        Returns:
            Path to generated MT940 file
        """
        mt940_filename = "matched_transactions.STA"
        mt940_path = os.path.join(temp_dir, mt940_filename)
        
        self.logger.debug(f"Generating MT940 file: {mt940_path}")
        
        return self.mt940_generator.generate_from_matches(matched_pairs, mt940_path)
        
    def _copy_matched_pdfs(self, matched_pairs: List[MatchResult], temp_dir: str) -> Dict[str, str]:
        """
        Copy PDF files for matched invoices to upload directory.
        
        Args:
            matched_pairs: List of matched transaction-invoice pairs
            temp_dir: Directory to copy PDF files to
            
        Returns:
            Dictionary mapping invoice numbers to copied PDF file paths
        """
        pdf_files = {}
        pdfs_dir = os.path.join(temp_dir, "pdfs")
        os.makedirs(pdfs_dir, exist_ok=True)
        
        self.logger.debug(f"Copying {len(matched_pairs)} PDF files to {pdfs_dir}")
        
        for i, match in enumerate(matched_pairs, 1):
            invoice = match.invoice
            invoice_number = invoice.invoice_number
            source_pdf_path = invoice.file_path
            
            # Report progress for each file
            self._report_progress(f"📄 Copying {i}/{len(matched_pairs)}: {invoice_number}")
            
            if not os.path.exists(source_pdf_path):
                self.logger.warning(f"PDF file not found: {source_pdf_path}")
                continue
                
            # Create destination filename
            pdf_filename = f"{invoice_number}.pdf"
            dest_pdf_path = os.path.join(pdfs_dir, pdf_filename)
            
            try:
                # Copy PDF file with error handling
                self._safe_copy_file(source_pdf_path, dest_pdf_path)
                pdf_files[invoice_number] = dest_pdf_path
                
                self.logger.debug(f"Copied PDF: {invoice_number} -> {dest_pdf_path}")
                
            except (IOError, OSError, PermissionError) as e:
                self.logger.error(f"Failed to copy PDF {source_pdf_path}: {e}")
                # Continue with other files
            except Exception as e:
                self.logger.error(f"Unexpected error copying PDF {source_pdf_path}: {e}")
                # Continue with other files
                
        self.logger.info(f"Successfully copied {len(pdf_files)} PDF files")
        return pdf_files
        
    def _create_transaction_mapping(self, matched_pairs: List[MatchResult]) -> Dict[str, str]:
        """
        Create mapping between transaction references and invoice numbers.
        
        Args:
            matched_pairs: List of matched transaction-invoice pairs
            
        Returns:
            Dictionary mapping transaction references to invoice numbers
        """
        mapping = {}
        
        for match in matched_pairs:
            transaction_ref = match.transaction.reference
            invoice_number = match.invoice.invoice_number
            
            mapping[transaction_ref] = invoice_number
            
        self.logger.debug(f"Created transaction mapping for {len(mapping)} pairs")
        return mapping
        
    def _cleanup_temp_directory(self, temp_dir: str):
        """
        Clean up temporary directory and all its contents.
        
        Args:
            temp_dir: Directory path to clean up
        """
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                self.logger.debug(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
            
    def cleanup_upload_package(self, upload_package: UploadDataPackage):
        """
        Clean up temporary files from an upload package.
        
        Args:
            upload_package: Package to clean up
        """
        self.logger.info(f"Cleaning up upload package: {upload_package.temp_directory}")
        self._cleanup_temp_directory(upload_package.temp_directory)
        
    def get_package_summary(self, upload_package: UploadDataPackage) -> str:
        """
        Get a human-readable summary of the upload package.
        
        Args:
            upload_package: Package to summarize
            
        Returns:
            Summary string
        """
        summary_lines = [
            f"Upload Package Summary:",
            f"  📄 MT940 file: {Path(upload_package.mt940_file_path).name}",
            f"  📁 PDF files: {len(upload_package.pdf_files)} files",
            f"  🔗 Total matches: {upload_package.total_matches}",
            f"  📂 Location: {upload_package.temp_directory}"
        ]
        
        return "\n".join(summary_lines)
    
    def _report_progress(self, message: str):
        """
        Report progress if callback is available.
        
        Args:
            message: Progress message to report
        """
        if self.progress_callback:
            self.progress_callback(message)
    
    def _safe_copy_file(self, source_path: str, dest_path: str, timeout: int = 30):
        """
        Safely copy a file with timeout and error handling.
        
        Args:
            source_path: Source file path
            dest_path: Destination file path
            timeout: Timeout in seconds for copy operation
            
        Raises:
            IOError: If copy operation fails
            TimeoutError: If copy operation takes too long
        """
        def timeout_handler(signum, frame):
            raise TimeoutError(f"File copy operation timed out after {timeout} seconds")
        
        # Set up timeout (Unix/Linux only - graceful fallback for Windows)
        old_handler = None
        try:
            if hasattr(signal, 'SIGALRM'):
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)
            
            # Perform the copy operation
            shutil.copy2(source_path, dest_path)
            
        except Exception as e:
            # Re-raise with more context
            raise IOError(f"Failed to copy {Path(source_path).name}: {e}")
        
        finally:
            # Clean up timeout handler
            if hasattr(signal, 'SIGALRM') and old_handler is not None:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)