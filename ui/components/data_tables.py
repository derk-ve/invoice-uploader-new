"""
Data tables component for structured display of transactions, invoices, and matches.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from decimal import Decimal

from ..styles.theme import AppTheme
from src.invoice_matching.core.models import Transaction, Invoice, MatchResult


class DataTable:
    """Base class for data table components."""
    
    def __init__(self, parent: ttk.Widget, title: str, columns: List[Tuple[str, str, int]]):
        """
        Initialize data table.
        
        Args:
            parent: Parent widget
            title: Table title
            columns: List of (column_id, column_name, width) tuples
        """
        self.parent = parent
        self.title = title
        self.columns = columns
        self.tree: Optional[ttk.Treeview] = None
        self.scrollbar: Optional[ttk.Scrollbar] = None
        self.container_frame: Optional[ttk.Frame] = None
        
    def setup_ui(self, row_start: int = 0) -> int:
        """
        Create the data table UI elements.
        
        Args:
            row_start: Starting row for grid layout
            
        Returns:
            Next available row number
        """
        current_row = row_start
        
        # Container frame
        self.container_frame = ttk.Frame(self.parent, style='Surface.TFrame')
        self.container_frame.grid(row=current_row, column=0, columnspan=4,
                                 sticky=(tk.W, tk.E, tk.N, tk.S),
                                 pady=(0, AppTheme.SPACING['lg']))
        current_row += 1
        
        # Configure grid weights
        self.container_frame.columnconfigure(0, weight=1)
        self.container_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            self.container_frame,
            text=self.title,
            style='Heading.TLabel'
        )
        title_label.grid(row=0, column=0, sticky=(tk.W, tk.N), 
                        pady=(AppTheme.SPACING['sm'], AppTheme.SPACING['sm']))
        
        # Table frame
        table_frame = ttk.Frame(self.container_frame, style='Surface.TFrame')
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create treeview
        column_ids = [col[0] for col in self.columns]
        self.tree = ttk.Treeview(
            table_frame,
            columns=column_ids,
            show='headings',
            style='Professional.Treeview',
            height=8
        )
        
        # Configure columns
        for col_id, col_name, width in self.columns:
            self.tree.heading(col_id, text=col_name)
            self.tree.column(col_id, width=width, anchor=tk.W)
        
        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Grid the treeview and scrollbar
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        return current_row
    
    def clear_data(self):
        """Clear all data from the table."""
        if self.tree:
            for item in self.tree.get_children():
                self.tree.delete(item)
    
    def add_row(self, values: List[str], tags: List[str] = None):
        """
        Add a row to the table.
        
        Args:
            values: List of values for each column
            tags: Optional tags for styling
        """
        if self.tree:
            self.tree.insert('', tk.END, values=values, tags=tags or [])


class MatchesTable(DataTable):
    """Table for displaying matched transaction-invoice pairs."""
    
    def __init__(self, parent: ttk.Widget):
        """Initialize matches table."""
        columns = [
            ('date', 'Date', 100),
            ('amount', 'Amount', 100),
            ('reference', 'Reference', 120),
            ('counterparty', 'Counterparty', 150),
            ('invoice_num', 'Invoice #', 120),
            ('pdf_file', 'PDF File', 200),
            ('confidence', 'Match %', 80)
        ]
        super().__init__(parent, "🎯 Matched Pairs", columns)
    
    def show_matches(self, matches: List[MatchResult]):
        """
        Display matched pairs in the table.
        
        Args:
            matches: List of match results to display
        """
        self.clear_data()
        
        if not matches:
            # Show empty state
            empty_values = ['', '', 'No matches found', '', '', '', '']
            self.add_row(empty_values, ['empty'])
            return
        
        for match in matches:
            # Format the data for display
            date_str = match.transaction.date.strftime('%Y-%m-%d')
            amount_str = f"€{match.transaction.amount:,.2f}"
            reference = self._truncate_text(match.transaction.reference, 15)
            
            # Use counterparty name if available, otherwise truncate description
            if match.transaction.counterparty_name:
                counterparty = self._truncate_text(match.transaction.counterparty_name, 20)
            else:
                counterparty = self._truncate_text(match.transaction.description, 20)
            
            invoice_num = match.invoice.invoice_number
            pdf_file = Path(match.invoice.file_path).name
            confidence = f"{match.confidence_score:.0%}"
            
            values = [date_str, amount_str, reference, counterparty, 
                     invoice_num, pdf_file, confidence]
            
            # Add color coding based on confidence
            tags = []
            if match.confidence_score >= 0.9:
                tags.append('high_confidence')
            elif match.confidence_score >= 0.7:
                tags.append('medium_confidence')
            else:
                tags.append('low_confidence')
            
            self.add_row(values, tags)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + '...'


class UnmatchedTransactionsTable(DataTable):
    """Table for displaying unmatched transactions."""
    
    def __init__(self, parent: ttk.Widget):
        """Initialize unmatched transactions table."""
        columns = [
            ('date', 'Date', 100),
            ('amount', 'Amount', 100), 
            ('reference', 'Reference', 120),
            ('counterparty', 'Counterparty', 200),
            ('description', 'Description', 300)
        ]
        super().__init__(parent, "💳 Unmatched Transactions", columns)
    
    def show_transactions(self, transactions: List[Transaction]):
        """
        Display unmatched transactions in the table.
        
        Args:
            transactions: List of unmatched transactions
        """
        self.clear_data()
        
        if not transactions:
            # Show empty state
            empty_values = ['', '', 'All transactions matched!', '', '']
            self.add_row(empty_values, ['empty'])
            return
        
        for transaction in transactions:
            date_str = transaction.date.strftime('%Y-%m-%d')
            amount_str = f"€{transaction.amount:,.2f}"
            reference = self._truncate_text(transaction.reference, 15)
            
            # Use counterparty name if available
            if transaction.counterparty_name:
                counterparty = self._truncate_text(transaction.counterparty_name, 25)
            else:
                counterparty = "Unknown"
            
            # Clean and truncate description (avoid full messy descriptions)
            description = self._clean_description(transaction.description, 40)
            
            values = [date_str, amount_str, reference, counterparty, description]
            self.add_row(values, ['unmatched'])
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + '...'
    
    def _clean_description(self, description: str, max_length: int) -> str:
        """Clean and truncate transaction description."""
        # Remove common noise from descriptions
        noise_patterns = [
            'SEPA Overboeking', 'SEPA OVERBOEKING', 'IBAN:', 'BIC:', 
            'Kenmerk:', 'Omschrijving:', '/TRTP/', '/REMI/', '/USTRD/'
        ]
        
        cleaned = description
        for pattern in noise_patterns:
            cleaned = cleaned.replace(pattern, ' ')
        
        # Clean up extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        # Truncate
        if len(cleaned) <= max_length:
            return cleaned
        return cleaned[:max_length-3] + '...'


class UnmatchedInvoicesTable(DataTable):
    """Table for displaying unmatched invoices."""
    
    def __init__(self, parent: ttk.Widget):
        """Initialize unmatched invoices table."""
        columns = [
            ('invoice_num', 'Invoice Number', 150),
            ('pdf_file', 'PDF Filename', 250),
            ('file_size', 'File Size', 100),
            ('file_path', 'File Path', 300)
        ]
        super().__init__(parent, "🧾 Unmatched Invoices", columns)
    
    def show_invoices(self, invoices: List[Invoice]):
        """
        Display unmatched invoices in the table.
        
        Args:
            invoices: List of unmatched invoices
        """
        self.clear_data()
        
        if not invoices:
            # Show empty state
            empty_values = ['', 'All invoices matched!', '', '']
            self.add_row(empty_values, ['empty'])
            return
        
        for invoice in invoices:
            invoice_num = invoice.invoice_number
            pdf_file = Path(invoice.file_path).name
            
            # Get file size if possible
            try:
                file_size = Path(invoice.file_path).stat().st_size
                if file_size > 1024 * 1024:  # MB
                    size_str = f"{file_size / (1024*1024):.1f} MB"
                elif file_size > 1024:  # KB
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size} B"
            except:
                size_str = "Unknown"
            
            # Truncate file path for display
            file_path = self._truncate_path(invoice.file_path, 40)
            
            values = [invoice_num, pdf_file, size_str, file_path]
            self.add_row(values, ['unmatched'])
    
    def _truncate_path(self, path: str, max_length: int) -> str:
        """Truncate file path intelligently."""
        if len(path) <= max_length:
            return path
        
        # Try to keep the filename and some parent dirs
        path_obj = Path(path)
        filename = path_obj.name
        parent_parts = path_obj.parent.parts
        
        if len(filename) >= max_length:
            return filename[:max_length-3] + '...'
        
        # Build truncated path
        available_length = max_length - len(filename) - 4  # -4 for "/.../"
        
        # Start from the end of parent parts
        truncated_parts = []
        current_length = 0
        
        for part in reversed(parent_parts):
            if current_length + len(part) + 1 <= available_length:
                truncated_parts.insert(0, part)
                current_length += len(part) + 1
            else:
                break
        
        if truncated_parts:
            truncated_path = '/' + '/'.join(truncated_parts) + '/.../' + filename
        else:
            truncated_path = '/.../' + filename
        
        return truncated_path