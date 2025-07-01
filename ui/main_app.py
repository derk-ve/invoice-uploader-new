#!/usr/bin/env python3
"""
Modular Tkinter UI for Invoice Matching

Clean, modular architecture with separated concerns:
- File selection handled by FileSelector component
- Results display handled by ResultsDisplay component  
- Business logic handled by MatchingController
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.logging_setup import LoggingSetup
from components.file_selector import FileSelector
from components.results_display import ResultsDisplay
from controllers.matching_controller import MatchingController


class InvoiceMatcherApp:
    """Main application class coordinating UI components and business logic."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Invoice Matcher")
        self.root.geometry("800x600")
        
        # Initialize logging
        LoggingSetup.setup_logging()
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        
        # Initialize components
        self._setup_components()
        
        # Setup UI layout
        self._setup_ui()
        
        # Connect callbacks
        self._connect_callbacks()
    
    def _setup_components(self):
        """Initialize all components and controllers."""
        # Main frame for components
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # Initialize components
        self.file_selector = FileSelector(self.main_frame)
        self.results_display = ResultsDisplay(self.main_frame)
        self.matching_controller = MatchingController()
        
        # UI state
        self.match_button = None
        self.status_label = None
    
    def _setup_ui(self):
        """Create the main UI layout."""
        # Configure main window grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(4, weight=1)  # Results area expands
        
        current_row = 0
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Invoice Matching Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=current_row, column=0, columnspan=3, pady=(0, 20))
        current_row += 1
        
        # File selector component
        current_row = self.file_selector.setup_ui(current_row)
        
        # Control panel (matching button and status)
        current_row = self._setup_control_panel(current_row)
        
        # Results display component
        self.results_display.setup_ui(current_row)
    
    def _setup_control_panel(self, row_start: int) -> int:
        """
        Setup the control panel with matching button and status.
        
        Args:
            row_start: Starting row for grid layout
            
        Returns:
            Next available row number
        """
        # Control panel frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=row_start, column=0, columnspan=3, pady=20)
        
        # Match button
        self.match_button = ttk.Button(button_frame, text="Run Matching", 
                                      command=self._on_run_matching, 
                                      style="Accent.TButton")
        self.match_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT)
        
        return row_start + 1
    
    def _connect_callbacks(self):
        """Connect component callbacks."""
        # File selector callbacks
        self.file_selector.set_files_changed_callback(self._on_files_changed)
        
        # Matching controller callbacks
        self.matching_controller.set_step_start_callback(self._on_step_start)
        self.matching_controller.set_transaction_loaded_callback(self._on_transaction_loaded)
        self.matching_controller.set_invoice_scanned_callback(self._on_invoice_scanned)
        self.matching_controller.set_summary_ready_callback(self._on_summary_ready)
        self.matching_controller.set_error_callback(self._on_error)
    
    def _on_files_changed(self, file_type: str, files: list):
        """
        Handle file selection changes.
        
        Args:
            file_type: Type of files selected ("mt940" or "pdf")
            files: List of selected file paths
        """
        # Show selected files in results
        display_type = "MT940" if file_type == "mt940" else "PDF"
        self.results_display.show_file_selection(display_type, files)
        
        self.logger.info(f"Selected {len(files)} {display_type} files")
    
    def _on_run_matching(self):
        """Handle run matching button click."""
        # Get selected files
        mt940_files = self.file_selector.get_mt940_files()
        pdf_files = self.file_selector.get_pdf_files()
        
        # Validate files
        error_message = self.matching_controller.validate_files(mt940_files, pdf_files)
        if error_message:
            messagebox.showerror("Error", error_message)
            return
        
        # Update UI state
        self._set_processing_state(True)
        
        # Clear previous results and start matching
        self.results_display.show_matching_start()
        
        try:
            # Run matching (this will trigger progress callbacks)
            summary = self.matching_controller.run_matching(mt940_files, pdf_files)
            
            if summary:
                # Show results
                self.results_display.show_matching_results(summary)
                self._set_status("Complete", "green")
            else:
                self._set_status("Error", "red")
                
        except Exception as e:
            self.logger.error(f"Unexpected error during matching: {e}")
            self.results_display.show_error(f"Unexpected error: {e}")
            self._set_status("Error", "red")
        
        finally:
            # Restore UI state
            self._set_processing_state(False)
    
    def _set_processing_state(self, processing: bool):
        """
        Update UI state for processing.
        
        Args:
            processing: True if processing, False if idle
        """
        if processing:
            self.match_button.config(state="disabled")
            self._set_status("Processing...", "orange")
        else:
            self.match_button.config(state="normal")
    
    def _set_status(self, text: str, color: str):
        """
        Update status label.
        
        Args:
            text: Status text
            color: Text color
        """
        if self.status_label:
            self.status_label.config(text=text, foreground=color)
    
    # Matching controller callback handlers
    def _on_step_start(self, step_name: str):
        """Handle step start notification."""
        self.results_display.show_step(step_name)
    
    def _on_transaction_loaded(self, file_path: str, count: int, success: bool):
        """Handle transaction loading progress."""
        self.results_display.show_transaction_loading(file_path, count, success)
    
    def _on_invoice_scanned(self, file_path: str, invoice_number: str):
        """Handle invoice scanning progress.""" 
        self.results_display.show_invoice_scanning(file_path, invoice_number)
    
    def _on_summary_ready(self, transaction_count: int, invoice_count: int):
        """Handle summary statistics."""
        self.results_display.show_summary_stats(transaction_count, invoice_count)
    
    def _on_error(self, error_message: str):
        """Handle error notifications."""
        self.results_display.show_error(error_message)
        self._set_status("Error", "red")


def main():
    """Run the application."""
    root = tk.Tk()
    app = InvoiceMatcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()