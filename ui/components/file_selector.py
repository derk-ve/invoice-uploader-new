"""
File selection component for MT940 and PDF files with professional styling.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import List, Callable, Optional

from ..styles.theme import AppTheme


class FileSelector:
    """Component for handling file selection UI and logic."""
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize file selector component.
        
        Args:
            parent: Parent widget to attach this component to
        """
        self.parent = parent
        self.mt940_files: List[str] = []
        self.pdf_files: List[str] = []
        
        # Callback functions for file selection events
        self.on_files_changed: Optional[Callable] = None
        
        # UI elements (will be created in setup_ui)
        self.mt940_label = None
        self.pdf_label = None
        
    def setup_ui(self, row_start: int = 0) -> int:
        """
        Create the file selection UI elements with professional styling.
        
        Args:
            row_start: Starting row for grid layout
            
        Returns:
            Next available row number
        """
        current_row = row_start
        
        # Configure grid columns for proper layout
        self.parent.columnconfigure(0, weight=0, minsize=200)  # Label column
        self.parent.columnconfigure(1, weight=0, minsize=150)  # Button column  
        self.parent.columnconfigure(2, weight=1)               # Status column
        
        # MT940 Files Section
        mt940_header = ttk.Label(
            self.parent, 
            text="MT940 Transaction Files:", 
            style='Heading.TLabel'
        )
        mt940_header.grid(
            row=current_row, column=0, 
            sticky=tk.W, 
            pady=(0, AppTheme.SPACING['xs']),
            padx=(0, AppTheme.SPACING['md'])
        )
        
        mt940_button = ttk.Button(
            self.parent, 
            text="Select MT940 Files", 
            command=self.select_mt940_files,
            style='Accent.TButton'
        )
        mt940_button.grid(
            row=current_row, column=1, 
            sticky=tk.W, 
            padx=(0, AppTheme.SPACING['md'])
        )
        
        self.mt940_label = ttk.Label(
            self.parent, 
            text="No files selected", 
            style='Secondary.TLabel'
        )
        self.mt940_label.grid(row=current_row, column=2, sticky=tk.W)
        
        current_row += 1
        
        # PDF Files Section
        pdf_header = ttk.Label(
            self.parent, 
            text="PDF Invoice Files:", 
            style='Heading.TLabel'
        )
        pdf_header.grid(
            row=current_row, column=0, 
            sticky=tk.W, 
            pady=(AppTheme.SPACING['md'], AppTheme.SPACING['xs']),
            padx=(0, AppTheme.SPACING['md'])
        )
        
        pdf_button = ttk.Button(
            self.parent, 
            text="Select PDF Files", 
            command=self.select_pdf_files,
            style='Accent.TButton'
        )
        pdf_button.grid(
            row=current_row, column=1, 
            sticky=tk.W, 
            pady=(AppTheme.SPACING['md'], 0),
            padx=(0, AppTheme.SPACING['md'])
        )
        
        self.pdf_label = ttk.Label(
            self.parent, 
            text="No files selected", 
            style='Secondary.TLabel'
        )
        self.pdf_label.grid(
            row=current_row, column=2, 
            sticky=tk.W, 
            pady=(AppTheme.SPACING['md'], 0)
        )
        
        return current_row + 1
    
    def select_mt940_files(self):
        """Handle MT940 file selection."""
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
            self.mt940_label.config(
                text=f"{AppTheme.get_icon('file')} {count} file{'s' if count != 1 else ''} selected"
            )
            # Update style to success color
            self.mt940_label.configure(style='Success.TLabel')
            
            # Trigger callback if set
            if self.on_files_changed:
                self.on_files_changed("mt940", self.mt940_files)
    
    def select_pdf_files(self):
        """Handle PDF file selection."""
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
            self.pdf_label.config(
                text=f"{AppTheme.get_icon('file')} {count} file{'s' if count != 1 else ''} selected"
            )
            # Update style to success color
            self.pdf_label.configure(style='Success.TLabel')
            
            # Trigger callback if set
            if self.on_files_changed:
                self.on_files_changed("pdf", self.pdf_files)
    
    def get_mt940_files(self) -> List[str]:
        """Get selected MT940 files."""
        return self.mt940_files.copy()
    
    def get_pdf_files(self) -> List[str]:
        """Get selected PDF files."""
        return self.pdf_files.copy()
    
    def has_mt940_files(self) -> bool:
        """Check if MT940 files are selected."""
        return len(self.mt940_files) > 0
    
    def has_pdf_files(self) -> bool:
        """Check if PDF files are selected."""
        return len(self.pdf_files) > 0
    
    def clear_selections(self):
        """Clear all file selections."""
        self.mt940_files = []
        self.pdf_files = []
        
        if self.mt940_label:
            self.mt940_label.config(text="No files selected")
            self.mt940_label.configure(style='Secondary.TLabel')
        if self.pdf_label:
            self.pdf_label.config(text="No files selected")
            self.pdf_label.configure(style='Secondary.TLabel')
    
    def set_files_changed_callback(self, callback: Callable[[str, List[str]], None]):
        """
        Set callback function to be called when files are selected.
        
        Args:
            callback: Function that takes (file_type, file_list) parameters
        """
        self.on_files_changed = callback