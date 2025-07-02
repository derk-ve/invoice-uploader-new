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

from src.utils.logging_setup import LoggingSetup
from .components.file_selector import FileSelector
from .components.results_display import ResultsDisplay
from .controllers.matching_controller import MatchingController
from .styles.theme import AppTheme


class InvoiceMatcherApp:
    """Main application class coordinating UI components and business logic."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("📊 Invoice Matcher")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Apply professional styling
        self.style = AppTheme.configure_styles(self.root)
        
        # Initialize logging
        LoggingSetup.setup_logging()
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        
        # Initialize components
        self._setup_components()
        
        # Setup UI layout
        self._setup_ui()
        
        # Connect callbacks
        self._connect_callbacks()
        
        # Apply final styling touches
        self._apply_final_styling()
    
    def _setup_components(self):
        """Initialize all components and controllers."""
        # Main frame for components with professional styling
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame', padding=AppTheme.SPACING['lg'])
        
        # Initialize components
        self.file_selector = FileSelector(self.main_frame)
        self.results_display = ResultsDisplay(self.main_frame)
        self.matching_controller = MatchingController()
        
        # UI state
        self.match_button = None
        self.status_label = None
        self.status_icon = None
    
    def _setup_ui(self):
        """Create the enhanced main UI layout."""
        # Configure main window grid for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid - single column layout for all components
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # Header row
        self.main_frame.rowconfigure(1, weight=0)  # File selector row  
        self.main_frame.rowconfigure(2, weight=0)  # Control panel row
        self.main_frame.rowconfigure(3, weight=1)  # Results area expands
        
        current_row = 0
        
        # Professional header section
        current_row = self._setup_header(current_row)
        
        # File selector component
        current_row = self.file_selector.setup_ui(current_row)
        
        # Control panel (matching button and status)
        current_row = self._setup_control_panel(current_row)
        
        # Results display component
        self.results_display.setup_ui(current_row)
    
    def _setup_header(self, row_start: int) -> int:
        """
        Setup the professional header section.
        
        Args:
            row_start: Starting row for grid layout
            
        Returns:
            Next available row number
        """
        # Header frame with professional styling
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        header_frame.grid(row=row_start, column=0, 
                         sticky=(tk.W, tk.E), pady=(0, AppTheme.SPACING['xl']))
        header_frame.configure(padding=AppTheme.SPACING['lg'])
        
        # App title with icon
        title_label = ttk.Label(
            header_frame, 
            text="📊 Invoice Matching Tool", 
            font=('Segoe UI', 20, 'bold'),
            foreground='white',
            background=AppTheme.COLORS['primary']
        )
        title_label.pack(side=tk.LEFT)
        
        # Version/subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Professional Edition - Advanced Invoice Processing",
            font=AppTheme.FONTS['body'],
            foreground='white',
            background=AppTheme.COLORS['primary']
        )
        subtitle_label.pack(side=tk.LEFT, padx=(AppTheme.SPACING['md'], 0))
        
        return row_start + 1
    
    def _setup_control_panel(self, row_start: int) -> int:
        """
        Setup the enhanced control panel with professional styling.
        
        Args:
            row_start: Starting row for grid layout
            
        Returns:
            Next available row number
        """
        # Control panel frame with main background styling (matching file selector)
        control_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        control_frame.grid(row=row_start, column=0, 
                          sticky=(tk.W, tk.E), 
                          pady=(AppTheme.SPACING['md'], AppTheme.SPACING['xl']))
        
        # Button container
        button_container = ttk.Frame(control_frame, style='Main.TFrame')
        button_container.pack(fill=tk.X)
        
        # Match button with light blue styling
        self.match_button = ttk.Button(
            button_container, 
            text=f"{AppTheme.get_icon('search')} Run Matching", 
            command=self._on_run_matching, 
            style="LightBlue.TButton"
        )
        self.match_button.pack(side=tk.LEFT, padx=(0, AppTheme.SPACING['md']))
        
        # Status with icon
        status_container = ttk.Frame(button_container, style='Main.TFrame')
        status_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # # Status icon
        # self.status_icon = ttk.Label(
        #     status_container, 
        #     text=AppTheme.get_icon('checkmark'), 
        #     style='Card.TLabel',
        #     font=AppTheme.FONTS['heading']
        # )
        # self.status_icon.pack(side=tk.LEFT, padx=(0, AppTheme.SPACING['xs']))
        
        # Status label with professional styling
        self.status_label = ttk.Label(
            status_container, 
            text="Upload files before running matching", 
            style='Body.TLabel'
        )
        self.status_label.pack(side=tk.LEFT)
        
        return row_start + 1
    
    def _apply_final_styling(self):
        """Apply final styling touches and optimizations."""
        # Configure additional treeview styling for tables
        self.style.configure(
            'Professional.Treeview',
            rowheight=28,  # Increase row height for better readability
            font=AppTheme.FONTS['body']
        )
        
        # Configure tag colors for treeview items
        self.style.configure(
            'Professional.Treeview.Item',
            foreground=AppTheme.COLORS['text_primary']
        )
        
        # Add alternating row colors
        self.style.configure(
            'Professional.Treeview',
            background=AppTheme.COLORS['surface'],
            fieldbackground=AppTheme.COLORS['surface']
        )
        
        # Configure notebook tab styling
        self.style.configure(
            'Professional.TNotebook.Tab',
            focuscolor='none'
        )
    
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
                self._set_status("Matching completed successfully", "success", "checkmark")
            else:
                self._set_status("Processing failed", "error", "error")
                
        except Exception as e:
            self.logger.error(f"Unexpected error during matching: {e}")
            self.results_display.show_error(f"Unexpected error: {e}")
            self._set_status("Error occurred", "error", "error")
        
        finally:
            # Restore UI state
            self._set_processing_state(False)
    
    def _set_processing_state(self, processing: bool):
        """
        Update UI state for processing with enhanced visual feedback.
        
        Args:
            processing: True if processing, False if idle
        """
        if processing:
            self.match_button.config(state="disabled")
            self._set_status("Processing...", "warning", "search")
        else:
            self.match_button.config(state="normal")
    
    def _set_status(self, text: str, status_type: str, icon_type: str = None):
        """
        Update status label with professional styling.
        
        Args:
            text: Status text
            status_type: Status type ('success', 'warning', 'error', 'info')
            icon_type: Icon type for the status
        """
        if self.status_label and self.status_icon:
            # Update text
            self.status_label.config(text=text)
            
            # Update icon
            if icon_type:
                self.status_icon.config(text=AppTheme.get_icon(icon_type))
            
            # Apply styling based on status type
            color_map = {
                'success': AppTheme.COLORS['success'],
                'warning': AppTheme.COLORS['warning'],
                'error': AppTheme.COLORS['error'],
                'info': AppTheme.COLORS['info']
            }
            
            color = color_map.get(status_type, AppTheme.COLORS['text_primary'])
            self.status_label.config(foreground=color)
            self.status_icon.config(foreground=color)
    
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
        self._set_status("Error occurred", "error", "error")


def main():
    """Run the application."""
    root = tk.Tk()
    app = InvoiceMatcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()