"""
Results display component for showing matching results and progress.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path
from typing import List, Optional

# Import for type hints
from src.invoice_matching.core.models import MatchingSummary


class ResultsDisplay:
    """Component for displaying matching results and progress updates."""
    
    def __init__(self, parent: ttk.Widget):
        """
        Initialize results display component.
        
        Args:
            parent: Parent widget to attach this component to
        """
        self.parent = parent
        self.results_text: Optional[scrolledtext.ScrolledText] = None
        
    def setup_ui(self, row_start: int = 0) -> int:
        """
        Create the results display UI elements.
        
        Args:
            row_start: Starting row for grid layout
            
        Returns:
            Next available row number
        """
        current_row = row_start
        
        # Results Section Label
        ttk.Label(self.parent, text="Results:", 
                 font=("Arial", 10, "bold")).grid(row=current_row, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        
        current_row += 1
        
        # Results Text Area
        self.results_text = scrolledtext.ScrolledText(self.parent, wrap=tk.WORD, width=80, height=20)
        self.results_text.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        # Show initial welcome message
        self.show_welcome_message()
        
        return current_row + 1
    
    def show_welcome_message(self):
        """Display initial welcome message."""
        self.clear()
        self.add_text("Welcome to Invoice Matcher!\n\n")
        self.add_text("1. Select your MT940 transaction files\n")
        self.add_text("2. Select your PDF invoice files\n")
        self.add_text("3. Click 'Run Matching' to process\n\n")
        self.add_text("Results will appear here...\n")
    
    def clear(self):
        """Clear all text from results display."""
        if self.results_text:
            self.results_text.delete(1.0, tk.END)
    
    def add_text(self, text: str):
        """
        Add text to results display.
        
        Args:
            text: Text to add
        """
        if self.results_text:
            self.results_text.insert(tk.END, text)
            self.results_text.see(tk.END)
    
    def add_line(self, text: str):
        """
        Add a line of text (with newline).
        
        Args:
            text: Text to add as a line
        """
        self.add_text(text + "\n")
    
    def update_display(self):
        """Force display update."""
        if self.results_text:
            self.results_text.update()
    
    def show_file_selection(self, file_type: str, files: List[str]):
        """
        Show selected files in results.
        
        Args:
            file_type: Type of files (e.g., "MT940", "PDF")
            files: List of selected file paths
        """
        count = len(files)
        icon = "📄" if file_type == "MT940" else "📁"
        self.add_line(f"\n{icon} Selected {count} {file_type} file(s):")
        
        for file in files:
            self.add_line(f"   • {Path(file).name}")
    
    def show_matching_start(self):
        """Show matching process start message."""
        self.clear()
        self.add_line("=== Invoice Matching Started ===\n")
    
    def show_step(self, step_name: str):
        """
        Show current processing step.
        
        Args:
            step_name: Name of the current step
        """
        self.add_line(f"{step_name}")
        self.update_display()
    
    def show_transaction_loading(self, file_path: str, count: int, success: bool = True):
        """
        Show transaction loading result for a file.
        
        Args:
            file_path: Path to the file
            count: Number of transactions loaded
            success: Whether loading was successful
        """
        filename = Path(file_path).name
        if success:
            self.add_line(f"   ✅ {filename}: {count} transactions")
        else:
            self.add_line(f"   ❌ {filename}: Error loading transactions")
        self.update_display()
    
    def show_invoice_scanning(self, file_path: str, invoice_number: Optional[str]):
        """
        Show invoice scanning result for a file.
        
        Args:
            file_path: Path to the PDF file
            invoice_number: Extracted invoice number (None if failed)
        """
        filename = Path(file_path).name
        if invoice_number:
            self.add_line(f"   ✅ {filename}: {invoice_number}")
        else:
            self.add_line(f"   ⚠️ {filename}: Could not extract invoice number")
        self.update_display()
    
    def show_summary_stats(self, transaction_count: int, invoice_count: int):
        """
        Show summary statistics.
        
        Args:
            transaction_count: Number of transactions loaded
            invoice_count: Number of invoices found
        """
        self.add_line(f"\n📊 Total transactions loaded: {transaction_count}")
        self.add_line(f"📊 Total invoices found: {invoice_count}\n")
        self.update_display()
    
    def show_matching_results(self, summary: MatchingSummary):
        """
        Display comprehensive matching results.
        
        Args:
            summary: Matching summary with all results
        """
        self.add_line("✅ Matching Complete!\n")
        
        # Results Summary
        self.add_line("📊 Results Summary:")
        self.add_line(f"   • Matched pairs: {len(summary.matched_pairs)}")
        self.add_line(f"   • Unmatched transactions: {len(summary.unmatched_transactions)}")
        self.add_line(f"   • Unmatched invoices: {len(summary.unmatched_invoices)}")
        self.add_line(f"   • Match rate: {summary.match_rate:.1f}%")
        self.add_line(f"   • Total matched amount: €{summary.total_matched_amount}\n")
        
        # Show matched pairs
        if summary.matched_pairs:
            self.add_line("🎯 Matched Pairs:")
            for i, match in enumerate(summary.matched_pairs, 1):
                self.add_line(f"   {i}. {match.transaction.reference} ↔ {match.invoice.invoice_number}")
                self.add_line(f"      Transaction: {match.transaction.description}")
                self.add_line(f"      PDF File: {Path(match.invoice.file_path).name}")
                self.add_line(f"      Amount: €{match.transaction.amount}\n")
        
        # Show unmatched invoices
        if summary.unmatched_invoices:
            self.add_line(f"📄 Unmatched Invoices ({len(summary.unmatched_invoices)}):")
            for invoice in summary.unmatched_invoices:
                self.add_line(f"   • {invoice.invoice_number} ({Path(invoice.file_path).name})")
            self.add_line("")
        
        self.add_line("=== Matching Complete ===")
        self.update_display()
    
    def show_error(self, error_message: str):
        """
        Show error message.
        
        Args:
            error_message: Error message to display
        """
        self.add_line(f"\n❌ Error: {error_message}")
        self.update_display()