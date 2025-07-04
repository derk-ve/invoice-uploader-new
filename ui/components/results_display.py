"""
Enhanced results display component with tabbed interface and professional styling.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path
from typing import List, Optional, Callable
from decimal import Decimal

from ..styles.theme import AppTheme
from .summary_cards import SummaryCards
from .data_tables import MatchesTable, UnmatchedTransactionsTable, UnmatchedInvoicesTable
from src.invoice_matching.core.models import MatchingSummary


class ResultsDisplay:
    """Enhanced component for displaying matching results with tabbed interface."""
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize results display component.
        
        Args:
            parent: Parent widget to attach this component to
        """
        self.parent = parent
        
        # UI components
        self.main_frame: Optional[ttk.Frame] = None
        self.summary_cards: Optional[SummaryCards] = None
        self.notebook: Optional[ttk.Notebook] = None
        self.progress_text: Optional[scrolledtext.ScrolledText] = None
        
        # Data table components
        self.matches_table: Optional[MatchesTable] = None
        self.unmatched_transactions_table: Optional[UnmatchedTransactionsTable] = None
        self.unmatched_invoices_table: Optional[UnmatchedInvoicesTable] = None
        
        # Current matching data
        self.current_summary: Optional[MatchingSummary] = None
        
        # Upload control components
        self.upload_frame: Optional[ttk.Frame] = None
        self.upload_button: Optional[ttk.Button] = None
        self.upload_status_label: Optional[ttk.Label] = None
        self.download_button: Optional[ttk.Button] = None
        
        # Download callback
        self.on_download_request: Optional[Callable[[str], None]] = None
        
    def setup_ui(self, row_start: int = 0) -> int:
        """
        Create the enhanced results display UI elements.
        
        Args:
            row_start: Starting row for grid layout
            
        Returns:
            Next available row number
        """
        current_row = row_start
        
        # Main container frame
        self.main_frame = ttk.Frame(self.parent, style='Main.TFrame')
        self.main_frame.grid(row=current_row, column=0, columnspan=4, 
                            sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive layout
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)  # Notebook area expands (now at row 1)
        
        container_row = 0
        
        # Summary cards section - now starts at row 0
        self.summary_cards = SummaryCards(self.main_frame)
        container_row = self.summary_cards.setup_ui(container_row)
        
        # Tabbed results section
        self._setup_tabbed_results(container_row)
        
        # Show initial welcome state
        self.show_welcome_message()
        
        return current_row + 1
    
    def _setup_tabbed_results(self, row_start: int):
        """
        Setup the tabbed interface for detailed results.
        
        Args:
            row_start: Starting row for the notebook
        """
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.main_frame, style='Professional.TNotebook')
        self.notebook.grid(row=row_start, column=0, columnspan=4, 
                          sticky=(tk.W, tk.E, tk.N, tk.S), 
                          pady=(0, AppTheme.SPACING['md']))
        
        # Tab 1: Progress/Log
        progress_frame = ttk.Frame(self.notebook, style='Surface.TFrame')
        self.notebook.add(progress_frame, text=f"{AppTheme.get_icon('info')} Progress")
        
        # Progress text area
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)
        
        self.progress_text = scrolledtext.ScrolledText(
            progress_frame, 
            wrap=tk.WORD,
            font=AppTheme.FONTS['body'],
            bg=AppTheme.COLORS['surface'],
            fg=AppTheme.COLORS['text_primary']
        )
        self.progress_text.grid(row=0, column=0, 
                               sticky=(tk.W, tk.E, tk.N, tk.S),
                               padx=AppTheme.SPACING['md'], 
                               pady=AppTheme.SPACING['md'])
        
        # Tab 2: Matches
        matches_frame = ttk.Frame(self.notebook, style='Surface.TFrame')
        self.notebook.add(matches_frame, text=f"{AppTheme.get_icon('match')} Matches")
        
        # Configure matches frame grid
        matches_frame.columnconfigure(0, weight=1)
        matches_frame.rowconfigure(0, weight=1)  # Table area expands
        matches_frame.rowconfigure(1, weight=0)  # Upload control area fixed
        
        # Matches table (takes most space)
        self.matches_table = MatchesTable(matches_frame)
        table_row = self.matches_table.setup_ui()
        
        # Set up deletion callback
        self.matches_table.set_matches_deleted_callback(self._on_matches_deleted)
        
        # Upload control area
        self._setup_upload_controls(matches_frame, table_row)
        
        # Tab 3: Unmatched Transactions
        unmatched_trans_frame = ttk.Frame(self.notebook, style='Surface.TFrame')
        self.notebook.add(unmatched_trans_frame, text=f"{AppTheme.get_icon('transaction')} Unmatched Transactions")
        self.unmatched_transactions_table = UnmatchedTransactionsTable(unmatched_trans_frame)
        self.unmatched_transactions_table.setup_ui()
        
        # Tab 4: Unmatched Invoices
        unmatched_inv_frame = ttk.Frame(self.notebook, style='Surface.TFrame')
        self.notebook.add(unmatched_inv_frame, text=f"{AppTheme.get_icon('invoice')} Unmatched Invoices")
        self.unmatched_invoices_table = UnmatchedInvoicesTable(unmatched_inv_frame)
        self.unmatched_invoices_table.setup_ui()
    
    def show_welcome_message(self):
        """Display initial welcome message."""
        self.clear_progress()
        self.add_progress_text("Welcome to Invoice Matcher! 🎉\n\n")
        self.add_progress_text("👆 Follow these steps:\n")
        self.add_progress_text("1. Select your MT940 transaction files\n")
        self.add_progress_text("2. Select your PDF invoice files\n")
        self.add_progress_text("3. Click 'Run Matching' to process\n\n")
        self.add_progress_text("📊 Results will appear in the tabs above...\n")
        
        # Show empty state in summary cards
        if self.summary_cards:
            self.summary_cards._show_empty_state()
    
    def clear_progress(self):
        """Clear progress text area."""
        if self.progress_text:
            self.progress_text.delete(1.0, tk.END)
    
    def add_progress_text(self, text: str):
        """
        Add text to progress display.
        
        Args:
            text: Text to add
        """
        if self.progress_text:
            self.progress_text.insert(tk.END, text)
            self.progress_text.see(tk.END)
    
    def add_progress_line(self, text: str):
        """
        Add a line of text to progress (with newline).
        
        Args:
            text: Text to add as a line
        """
        self.add_progress_text(text + "\n")
    
    def update_display(self):
        """Force display update."""
        if self.progress_text:
            self.progress_text.update()
    
    # Backward compatibility methods (redirect to progress)
    def clear(self):
        """Clear all displays."""
        self.clear_progress()
    
    def add_text(self, text: str):
        """Add text (backward compatibility)."""
        self.add_progress_text(text)
    
    def add_line(self, text: str):
        """Add line (backward compatibility)."""
        self.add_progress_line(text)
    
    def show_file_selection(self, file_type: str, files: List[str]):
        """
        Show selected files in progress.
        
        Args:
            file_type: Type of files (e.g., "MT940", "PDF")
            files: List of selected file paths
        """
        count = len(files)
        icon = AppTheme.get_icon('file') if file_type == "MT940" else AppTheme.get_icon('folder')
        self.add_progress_line(f"\n{icon} Selected {count} {file_type} file(s):")
        
        for file in files:
            self.add_progress_line(f"   • {Path(file).name}")
    
    def show_matching_start(self):
        """Show matching process start message."""
        self.clear_progress()
        self.add_progress_line("=== Invoice Matching Started ===\n")
        
        # Show processing state in summary cards
        if self.summary_cards:
            self.summary_cards.show_processing()
    
    def show_step(self, step_name: str):
        """
        Show current processing step.
        
        Args:
            step_name: Name of the current step
        """
        self.add_progress_line(f"{step_name}")
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
            self.add_progress_line(f"   ✅ {filename}: {count} transactions")
        else:
            self.add_progress_line(f"   ❌ {filename}: Error loading transactions")
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
            self.add_progress_line(f"   ✅ {filename}: {invoice_number}")
        else:
            self.add_progress_line(f"   ⚠️ {filename}: Could not extract invoice number")
        self.update_display()
    
    def show_summary_stats(self, transaction_count: int, invoice_count: int):
        """
        Show summary statistics.
        
        Args:
            transaction_count: Number of transactions loaded
            invoice_count: Number of invoices found
        """
        self.add_progress_line(f"\n📊 Total transactions loaded: {transaction_count}")
        self.add_progress_line(f"📊 Total invoices found: {invoice_count}\n")
        self.update_display()
    
    def show_matching_results(self, summary: MatchingSummary):
        """
        Display comprehensive matching results in tabs and cards.
        
        Args:
            summary: Matching summary with all results
        """
        # Store current summary for deletion handling
        self.current_summary = summary
        
        # Update progress log
        self.add_progress_line("✅ Matching Complete!\n")
        self.add_progress_line("📊 Check the summary cards and tabs above for detailed results.")
        self.add_progress_line("=== Matching Complete ===")
        
        # Update all components
        self._refresh_all_data()
        
        # Enable download button if there are matches
        self.enable_download(bool(summary.matched_pairs))
        
        # Switch to matches tab if there are any matches
        if summary.matched_pairs and self.notebook:
            self.notebook.select(1)  # Select matches tab
        
        self.update_display()
    
    def show_error(self, error_message: str):
        """
        Show error message.
        
        Args:
            error_message: Error message to display
        """
        self.add_progress_line(f"\n❌ Error: {error_message}")
        
        # Show error in summary cards
        if self.summary_cards:
            self.summary_cards.show_error(error_message)
        
        self.update_display()
    
    def _refresh_all_data(self):
        """
        Refresh all UI components with current summary data.
        """
        if not self.current_summary:
            return
        
        # Update summary cards
        if self.summary_cards:
            self.summary_cards.show_summary(self.current_summary)
        
        # Update data tables
        if self.matches_table:
            self.matches_table.show_matches(self.current_summary.matched_pairs)
        
        if self.unmatched_transactions_table:
            self.unmatched_transactions_table.show_transactions(self.current_summary.unmatched_transactions)
        
        if self.unmatched_invoices_table:
            self.unmatched_invoices_table.show_invoices(self.current_summary.unmatched_invoices)
    
    def _on_matches_deleted(self, deleted_matches):
        """
        Handle deletion of matches by updating the summary and refreshing UI.
        
        Args:
            deleted_matches: List of MatchResult objects that were deleted
        """
        if not self.current_summary or not deleted_matches:
            return
        
        # Remove deleted matches from summary
        for deleted_match in deleted_matches:
            if deleted_match in self.current_summary.matched_pairs:
                self.current_summary.matched_pairs.remove(deleted_match)
                
                # Add transaction and invoice back to unmatched lists
                self.current_summary.unmatched_transactions.append(deleted_match.transaction)
                self.current_summary.unmatched_invoices.append(deleted_match.invoice)
        
        # Recalculate summary statistics
        self._recalculate_summary_stats()
        
        # Refresh all UI components
        self._refresh_all_data()
        
        # Log the deletion
        count = len(deleted_matches)
        if count == 1:
            self.add_progress_line(f"\n🗑️ Deleted 1 match")
        else:
            self.add_progress_line(f"\n🗑️ Deleted {count} matches")
        
        self.update_display()
    
    def _recalculate_summary_stats(self):
        """
        Recalculate summary statistics after deletions.
        """
        if not self.current_summary:
            return
        
        # Update counts
        self.current_summary.total_invoices = len(self.current_summary.matched_pairs) + len(self.current_summary.unmatched_invoices)
        
        # Recalculate match rate
        if self.current_summary.total_transactions > 0:
            self.current_summary.match_rate = (len(self.current_summary.matched_pairs) / self.current_summary.total_transactions) * 100
        else:
            self.current_summary.match_rate = 0.0
        
        # Recalculate total matched amount
        if self.current_summary.matched_pairs:
            self.current_summary.total_matched_amount = sum(
                match.transaction.amount for match in self.current_summary.matched_pairs
            )
        else:
            self.current_summary.total_matched_amount = Decimal('0')
    
    def _setup_upload_controls(self, parent_frame: ttk.Frame, row_start: int):
        """
        Setup upload control area in the matches tab.
        
        Args:
            parent_frame: Parent frame to attach controls to
            row_start: Starting row for grid layout
        """
        # Upload control frame
        self.upload_frame = ttk.Frame(parent_frame, style='Card.TFrame')
        self.upload_frame.grid(row=row_start, column=0, 
                              sticky=(tk.W, tk.E), 
                              padx=AppTheme.SPACING['md'], 
                              pady=AppTheme.SPACING['md'])
        
        # Configure grid
        self.upload_frame.columnconfigure(1, weight=1)
        
        # Upload section title
        title_label = ttk.Label(
            self.upload_frame, 
            text="📤 SnelStart Upload", 
            style='Heading.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=3, 
                        sticky=(tk.W, tk.N), pady=(0, AppTheme.SPACING['sm']))
        
        # Upload button
        self.upload_button = ttk.Button(
            self.upload_frame, 
            text="📤 Prepare Upload to SnelStart", 
            style="LightBlue.TButton",
            state="disabled"  # Initially disabled
        )
        self.upload_button.grid(row=1, column=0, 
                               padx=(0, AppTheme.SPACING['md']), 
                               pady=AppTheme.SPACING['sm'])
        
        # Download button
        self.download_button = ttk.Button(
            self.upload_frame, 
            text="💾 Download Package", 
            command=self._on_download_click,
            style="LightBlue.TButton",
            state="disabled"  # Initially disabled
        )
        self.download_button.grid(row=2, column=0, 
                                 padx=(0, AppTheme.SPACING['md']), 
                                 pady=(0, AppTheme.SPACING['sm']))
        
        # Upload status label
        self.upload_status_label = ttk.Label(
            self.upload_frame, 
            text="Connect to SnelStart first to enable upload", 
            style='Body.TLabel'
        )
        self.upload_status_label.grid(row=1, column=1, 
                                     sticky=(tk.W, tk.E), 
                                     padx=AppTheme.SPACING['sm'],
                                     pady=AppTheme.SPACING['sm'])
        
        # Info label
        info_label = ttk.Label(
            self.upload_frame,
            text="ℹ️ Upload sends files to SnelStart • Download creates a package for manual upload",
            style='Small.TLabel',
            foreground=AppTheme.COLORS['text_secondary']
        )
        info_label.grid(row=3, column=0, columnspan=3, 
                       sticky=(tk.W, tk.E), 
                       pady=(AppTheme.SPACING['xs'], 0))
    
    def update_upload_status(self, snelstart_ready: bool, status_message: str):
        """
        Update upload button and status based on SnelStart connection state.
        
        Args:
            snelstart_ready: True if SnelStart is ready for upload
            status_message: Status message to display
        """
        if self.upload_button and self.upload_status_label:
            if snelstart_ready:
                self.upload_button.config(state="normal")
                self.upload_button.config(text="📤 Upload to SnelStart")
                self.upload_status_label.config(
                    text=status_message,
                    foreground=AppTheme.COLORS['success']
                )
            else:
                self.upload_button.config(state="disabled")
                self.upload_button.config(text="📤 Prepare Upload to SnelStart")
                self.upload_status_label.config(
                    text=status_message,
                    foreground=AppTheme.COLORS['text_secondary']
                )
    
    def set_upload_callback(self, callback):
        """
        Set callback for upload button clicks.
        
        Args:
            callback: Function to call when upload button is clicked
        """
        if self.upload_button:
            self.upload_button.config(command=callback)
    
    def _on_download_click(self):
        """Handle download button click."""
        try:
            if not self.current_summary or not self.current_summary.matched_pairs:
                messagebox.showwarning("No Matches", "No matched pairs available for download.")
                return
            
            # Ask user to select download directory
            download_dir = filedialog.askdirectory(
                title="Select Download Location",
                mustexist=True
            )
            
            if not download_dir:
                return  # User cancelled
            
            # Show progress message
            self.add_progress_line(f"\n💾 Preparing download package...")
            self.add_progress_line(f"📂 Download location: {download_dir}")
            
            # Call the download callback if set
            if self.on_download_request:
                self.on_download_request(download_dir)
                
        except Exception as e:
            self.show_error(f"Download error: {e}")
    
    def set_download_callback(self, callback: Callable[[str], None]):
        """
        Set callback for download requests.
        
        Args:
            callback: Function to call when download is requested with download directory
        """
        self.on_download_request = callback
    
    def enable_download(self, enabled: bool = True):
        """
        Enable or disable the download button.
        
        Args:
            enabled: True to enable, False to disable
        """
        if self.download_button:
            state = "normal" if enabled else "disabled"
            self.download_button.config(state=state)
    
    def show_download_success(self, package_path: str, pdf_count: int):
        """
        Show download success message.
        
        Args:
            package_path: Path to the created package
            pdf_count: Number of PDF files in the package
        """
        self.add_progress_line(f"\n✅ Download package created successfully!")
        self.add_progress_line(f"📂 Location: {package_path}")
        self.add_progress_line(f"📄 Contents: 1 MT940 file + {pdf_count} PDF files")
        self.add_progress_line(f"🚀 Ready for manual upload to SnelStart!")
        self.update_display()