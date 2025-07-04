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
from .controllers.snelstart_controller import SnelStartController, SnelStartConnectionState
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
        # Create scrollable canvas setup
        self.canvas = tk.Canvas(self.root, bg=AppTheme.COLORS['background'])
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create the scrollable frame inside the canvas
        self.scrollable_frame = ttk.Frame(self.canvas, style='Main.TFrame')
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Main frame for components with professional styling (now inside scrollable frame)
        self.main_frame = ttk.Frame(self.scrollable_frame, style='Main.TFrame', padding=AppTheme.SPACING['lg'])
        
        # Initialize components
        self.file_selector = FileSelector(self.main_frame)
        self.results_display = ResultsDisplay(self.main_frame)
        self.matching_controller = MatchingController()
        self.snelstart_controller = SnelStartController()
        
        # UI state
        self.match_button = None
        self.snelstart_button = None
        self.status_label = None
        self.status_icon = None
    
    def _setup_ui(self):
        """Create the enhanced main UI layout with scrollable canvas."""
        # Configure main window grid for scrollable design
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)  # Scrollbar column
        self.root.rowconfigure(0, weight=1)
        
        # Place canvas and scrollbar
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure scrollable frame
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.rowconfigure(0, weight=1)
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
        
        # Configure scroll region and bindings
        self._configure_scrolling()
    
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
            text="Royal Canin Invoice Processing",
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
        
        # Configure control frame grid for vertical button layout (like file selector)
        control_frame.columnconfigure(0, weight=0, minsize=150)  # Button column
        control_frame.columnconfigure(1, weight=1)               # Status column
        
        # Row 0: Run Matching button (top button)
        self.match_button = ttk.Button(
            control_frame, 
            text=f"{AppTheme.get_icon('search')} Run Matching", 
            command=self._on_run_matching, 
            style="LightBlue.TButton"
        )
        self.match_button.grid(
            row=0, column=0, 
            sticky=tk.W, 
            pady=(0, AppTheme.SPACING['sm']),
            padx=(0, AppTheme.SPACING['md'])
        )

        # Status container spans both button rows in column 1
        status_container = ttk.Frame(control_frame, style='Main.TFrame')
        status_container.grid(
            row=0, column=1, 
            sticky=(tk.W, tk.E, tk.N), 
            padx=(AppTheme.SPACING['md'], 0)
        )

        # Status label with professional styling
        self.status_label = ttk.Label(
            status_container, 
            text="Upload files before running matching", 
            style='Secondary.TLabel'
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Row 1: Connect SnelStart button (bottom button)
        self.snelstart_button = ttk.Button(
            control_frame, 
            text=f"🏢 Connect SnelStart", 
            command=self._on_connect_snelstart, 
            style="LightBlue.TButton"
        )
        self.snelstart_button.grid(
            row=1, column=0, 
            sticky=tk.W, 
            pady=(0, AppTheme.SPACING['md']),
            padx=(0, AppTheme.SPACING['md'])
        )
        
        
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
        self.matching_controller.set_download_progress_callback(self._on_download_progress)
        
        # Results display callbacks
        self.results_display.set_download_callback(self._on_download_request)
        
        # SnelStart controller callbacks
        self.snelstart_controller.set_connection_start_callback(self._on_snelstart_step)
        self.snelstart_controller.set_connection_established_callback(self._on_snelstart_step)
        self.snelstart_controller.set_upload_ready_callback(self._on_snelstart_step)
        self.snelstart_controller.set_state_changed_callback(self._on_snelstart_state_changed)
        self.snelstart_controller.set_error_callback(self._on_snelstart_error)
    
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
        
        # Update scroll region after content changes
        self.root.after(50, self._update_scroll_region)
    
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
                # Update scroll region after results are displayed
                self.root.after(200, self._update_scroll_region)
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
        # Update scroll region after content changes
        self.root.after(50, self._update_scroll_region)
    
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
    
    def _on_download_progress(self, progress_message: str):
        """Handle download progress notifications."""
        self.results_display.show_step(progress_message)
    
    def _on_download_request(self, download_path: str):
        """Handle download package request."""
        try:
            # Get current matching summary from results display
            current_summary = self.results_display.current_summary
            
            if not current_summary:
                self.results_display.show_error("No matching results available for download.")
                return
            
            # Show progress in Progress tab
            self.results_display.show_step("💾 Starting download preparation...")
            
            # Prepare download package using controller
            package = self.matching_controller.prepare_download_package(current_summary, download_path)
            
            if package:
                # Show success message
                self.results_display.show_download_success(package.temp_directory, len(package.pdf_files))
                self._set_status("Download completed successfully", "success", "checkmark")
            else:
                self._set_status("Download failed", "error", "error")
                
        except Exception as e:
            self.logger.error(f"Download request error: {e}")
            self.results_display.show_error(f"Download failed: {e}")
            self._set_status("Download error", "error", "error")
    
    # SnelStart controller callback handlers
    def _on_connect_snelstart(self):
        """Handle SnelStart open button click."""
        # Update UI state
        self._set_snelstart_processing_state(True)
        
        # Show start of SnelStart workflow in results
        self.results_display.show_step("🏢 Opening SnelStart...")
        
        try:
            # Simply open/connect to SnelStart (user will handle the rest)
            success = self.snelstart_controller.open_snelstart()
            
            if success:
                self._update_snelstart_button_state()
                self._set_status("SnelStart opened - waiting for navigation", "info", "info")
            else:
                self._set_status("Failed to open SnelStart", "error", "error")
                
        except Exception as e:
            self.logger.error(f"Unexpected error opening SnelStart: {e}")
            self.results_display.show_error(f"SnelStart error: {e}")
            self._set_status("SnelStart error occurred", "error", "error")
        
        finally:
            # Restore UI state
            self._set_snelstart_processing_state(False)
    
    def _on_snelstart_step(self, message: str):
        """Handle SnelStart step notifications."""
        self.results_display.show_step(f"🏢 {message}")
    
    def _on_snelstart_state_changed(self, state: SnelStartConnectionState, message: str):
        """Handle SnelStart state change notifications."""
        self.logger.info(f"SnelStart state: {state.value} - {message}")
        self._update_snelstart_button_state()
        
        # Update results display upload status
        is_ready = state == SnelStartConnectionState.READY_FOR_UPLOAD
        self.results_display.update_upload_status(is_ready, message)
    
    def _on_snelstart_error(self, error_message: str):
        """Handle SnelStart error notifications."""
        self.results_display.show_error(f"SnelStart: {error_message}")
        self._set_status("SnelStart error", "error", "error")
    
    def _set_snelstart_processing_state(self, processing: bool):
        """
        Update SnelStart UI state for processing.
        
        Args:
            processing: True if processing, False if idle
        """
        if processing:
            self.snelstart_button.config(state="disabled")
            self._set_status("Connecting to SnelStart...", "warning", "search")
        else:
            self.snelstart_button.config(state="normal")
    
    def _update_snelstart_button_state(self):
        """Update SnelStart button text and state based on connection status."""
        state = self.snelstart_controller.get_connection_state()
        
        if state == SnelStartConnectionState.DISCONNECTED:
            self.snelstart_button.config(text="🏢 Connect SnelStart")
        elif state == SnelStartConnectionState.CONNECTING:
            self.snelstart_button.config(text="🏢 Connecting...")
        elif state == SnelStartConnectionState.CONNECTED:
            self.snelstart_button.config(text="🏢 Waiting for Navigation")
        elif state == SnelStartConnectionState.READY_FOR_UPLOAD:
            self.snelstart_button.config(text="🏢 Ready for Upload")
        elif state == SnelStartConnectionState.ERROR:
            self.snelstart_button.config(text="🏢 Connection Error")
        else:
            self.snelstart_button.config(text=f"🏢 {state.value.title()}")
    
    def _configure_scrolling(self):
        """Configure scrolling behavior and event bindings."""
        # Update scroll region when content changes
        self.scrollable_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        
        # Update scroll region initially
        self.root.after(100, self._update_scroll_region)
    
    def _on_frame_configure(self, event):
        """Update scroll region when frame size changes."""
        self._update_scroll_region()
    
    def _on_canvas_configure(self, event):
        """Update canvas window width when canvas is resized."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        # Check if scrolling is needed
        if self.canvas.cget("scrollregion"):
            # Different systems handle mouse wheel differently
            if event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")
    
    def _update_scroll_region(self):
        """Update the scroll region to encompass all content."""
        # Update the canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Hide scrollbar if content fits in window
        canvas_height = self.canvas.winfo_height()
        content_height = self.scrollable_frame.winfo_reqheight()
        
        if content_height <= canvas_height:
            self.scrollbar.grid_remove()
        else:
            self.scrollbar.grid()


def main():
    """Run the application."""
    root = tk.Tk()
    app = InvoiceMatcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()