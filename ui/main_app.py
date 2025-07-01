#!/usr/bin/env python3
"""
Simple Tkinter UI for Invoice Matching

Essential functionality only:
- File selection for MT940 and PDF files
- Run matching button
- Basic results display
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from invoice_matching import PDFScanner, parse_mt940_file, do_bookkeeping
from utils.logging_setup import LoggingSetup

class InvoiceMatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Matcher")
        self.root.geometry("800x600")
        
        # Initialize logging
        LoggingSetup.setup_logging()
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        
        # File storage
        self.mt940_files = []
        self.pdf_files = []
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create the main UI layout."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Invoice Matching Tool", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # MT940 Files Section
        ttk.Label(main_frame, text="MT940 Transaction Files:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Button(main_frame, text="Select MT940 Files", command=self.select_mt940_files).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        self.mt940_label = ttk.Label(main_frame, text="No files selected", foreground="gray")
        self.mt940_label.grid(row=1, column=2, sticky=tk.W, padx=(10, 0))
        
        # PDF Files Section
        ttk.Label(main_frame, text="PDF Invoice Files:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        ttk.Button(main_frame, text="Select PDF Files", command=self.select_pdf_files).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        self.pdf_label = ttk.Label(main_frame, text="No files selected", foreground="gray")
        self.pdf_label.grid(row=2, column=2, sticky=tk.W, padx=(10, 0))
        
        # Matching Section
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.match_button = ttk.Button(button_frame, text="Run Matching", command=self.run_matching, style="Accent.TButton")
        self.match_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_label = ttk.Label(button_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT)
        
        # Results Section
        ttk.Label(main_frame, text="Results:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        
        self.results_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=20)
        self.results_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        
        # Initial message
        self.results_text.insert(tk.END, "Welcome to Invoice Matcher!\n\n")
        self.results_text.insert(tk.END, "1. Select your MT940 transaction files\n")
        self.results_text.insert(tk.END, "2. Select your PDF invoice files\n")
        self.results_text.insert(tk.END, "3. Click 'Run Matching' to process\n\n")
        self.results_text.insert(tk.END, "Results will appear here...\n")
        
    def select_mt940_files(self):
        """Select MT940 files."""
        filetypes = [
            ("MT940 files", "*.STA *.MT940 *.mt940"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select MT940 Transaction Files",
            filetypes=filetypes
        )
        
        if files:
            self.mt940_files = list(files)
            count = len(self.mt940_files)
            self.mt940_label.config(text=f"{count} file{'s' if count != 1 else ''} selected", foreground="black")
            self.logger.info(f"Selected {count} MT940 files")
            
            # Show selected files in results
            self.results_text.insert(tk.END, f"\n📄 Selected {count} MT940 file(s):\n")
            for file in self.mt940_files:
                self.results_text.insert(tk.END, f"   • {Path(file).name}\n")
            self.results_text.see(tk.END)
        
    def select_pdf_files(self):
        """Select PDF files."""
        filetypes = [
            ("PDF files", "*.pdf *.PDF"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select PDF Invoice Files",
            filetypes=filetypes
        )
        
        if files:
            self.pdf_files = list(files)
            count = len(self.pdf_files)
            self.pdf_label.config(text=f"{count} file{'s' if count != 1 else ''} selected", foreground="black")
            self.logger.info(f"Selected {count} PDF files")
            
            # Show selected files in results
            self.results_text.insert(tk.END, f"\n📁 Selected {count} PDF file(s):\n")
            for file in self.pdf_files:
                self.results_text.insert(tk.END, f"   • {Path(file).name}\n")
            self.results_text.see(tk.END)
    
    def run_matching(self):
        """Run the invoice matching process."""
        # Validation
        if not self.mt940_files:
            messagebox.showerror("Error", "Please select MT940 transaction files first.")
            return
            
        if not self.pdf_files:
            messagebox.showerror("Error", "Please select PDF invoice files first.")
            return
        
        try:
            self.status_label.config(text="Processing...", foreground="orange")
            self.match_button.config(state="disabled")
            self.root.update()
            
            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "=== Invoice Matching Started ===\n\n")
            self.root.update()
            
            # Step 1: Load transactions
            self.results_text.insert(tk.END, "📄 Loading transactions from MT940 files...\n")
            self.root.update()
            
            transactions = []
            for mt940_file in self.mt940_files:
                try:
                    file_transactions = parse_mt940_file(mt940_file)
                    transactions.extend(file_transactions)
                    self.results_text.insert(tk.END, f"   ✅ {Path(mt940_file).name}: {len(file_transactions)} transactions\n")
                except Exception as e:
                    self.results_text.insert(tk.END, f"   ❌ {Path(mt940_file).name}: Error - {e}\n")
                self.root.update()
            
            if not transactions:
                self.results_text.insert(tk.END, "\n❌ No transactions loaded. Check your MT940 files.\n")
                return
                
            self.results_text.insert(tk.END, f"\n📊 Total transactions loaded: {len(transactions)}\n\n")
            self.root.update()
            
            # Step 2: Scan invoices
            self.results_text.insert(tk.END, "📁 Scanning PDF invoices...\n")
            self.root.update()
            
            all_invoices = []
            for pdf_file in self.pdf_files:
                try:
                    # Create a temporary directory for each file and scan it
                    temp_dir = str(Path(pdf_file).parent)
                    scanner = PDFScanner(temp_dir)
                    file_invoices = scanner.scan()
                    
                    # Filter to only include the current file
                    file_invoices = [inv for inv in file_invoices if inv.file_path == pdf_file]
                    all_invoices.extend(file_invoices)
                    
                    if file_invoices:
                        self.results_text.insert(tk.END, f"   ✅ {Path(pdf_file).name}: {file_invoices[0].invoice_number}\n")
                    else:
                        self.results_text.insert(tk.END, f"   ⚠️ {Path(pdf_file).name}: Could not extract invoice number\n")
                except Exception as e:
                    self.results_text.insert(tk.END, f"   ❌ {Path(pdf_file).name}: Error - {e}\n")
                self.root.update()
            
            if not all_invoices:
                self.results_text.insert(tk.END, "\n❌ No invoices found. Check your PDF files.\n")
                return
                
            self.results_text.insert(tk.END, f"\n📊 Total invoices found: {len(all_invoices)}\n\n")
            self.root.update()
            
            # Step 3: Run matching
            self.results_text.insert(tk.END, "🔍 Running matching algorithm...\n")
            self.root.update()
            
            summary = do_bookkeeping(transactions, all_invoices)
            
            # Step 4: Display results
            self.results_text.insert(tk.END, f"\n✅ Matching Complete!\n\n")
            self.results_text.insert(tk.END, f"📊 Results Summary:\n")
            self.results_text.insert(tk.END, f"   • Matched pairs: {len(summary.matched_pairs)}\n")
            self.results_text.insert(tk.END, f"   • Unmatched transactions: {len(summary.unmatched_transactions)}\n")
            self.results_text.insert(tk.END, f"   • Unmatched invoices: {len(summary.unmatched_invoices)}\n")
            self.results_text.insert(tk.END, f"   • Match rate: {summary.match_rate:.1f}%\n")
            self.results_text.insert(tk.END, f"   • Total matched amount: €{summary.total_matched_amount}\n\n")
            
            # Show matched pairs
            if summary.matched_pairs:
                self.results_text.insert(tk.END, f"🎯 Matched Pairs:\n")
                for i, match in enumerate(summary.matched_pairs, 1):
                    self.results_text.insert(tk.END, f"   {i}. {match.transaction.reference} ↔ {match.invoice.invoice_number}\n")
                    self.results_text.insert(tk.END, f"      Transaction: {match.transaction.description}\n")
                    self.results_text.insert(tk.END, f"      PDF File: {Path(match.invoice.file_path).name}\n")
                    self.results_text.insert(tk.END, f"      Amount: €{match.transaction.amount}\n\n")
            
            # Show unmatched invoices
            if summary.unmatched_invoices:
                self.results_text.insert(tk.END, f"📄 Unmatched Invoices ({len(summary.unmatched_invoices)}):\n")
                for invoice in summary.unmatched_invoices:
                    self.results_text.insert(tk.END, f"   • {invoice.invoice_number} ({Path(invoice.file_path).name})\n")
                self.results_text.insert(tk.END, "\n")
            
            self.results_text.insert(tk.END, "=== Matching Complete ===\n")
            self.status_label.config(text="Complete", foreground="green")
            
        except Exception as e:
            self.results_text.insert(tk.END, f"\n❌ Error during matching: {e}\n")
            self.status_label.config(text="Error", foreground="red")
            self.logger.error(f"Matching error: {e}")
            
        finally:
            self.match_button.config(state="normal")
            self.results_text.see(tk.END)

def main():
    """Run the application."""
    root = tk.Tk()
    app = InvoiceMatcherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()