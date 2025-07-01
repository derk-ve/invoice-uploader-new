"""
Centralized theme and styling for the Invoice Matcher application.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class AppTheme:
    """Centralized theme management for professional UI styling."""
    
    # Professional color palette
    COLORS = {
        # Primary colors
        'primary': '#2E86AB',           # Professional blue
        'primary_light': '#A23B72',     # Light accent
        'primary_dark': '#1D5F8A',      # Dark blue
        
        # Accent colors
        'accent': '#F18F01',            # Orange accent
        'accent_light': '#FCE4A6',      # Light orange
        
        # Status colors
        'success': '#4CAF50',           # Green for success
        'success_light': '#E8F5E8',     # Light green background
        'warning': '#FF9800',           # Orange for warnings
        'warning_light': '#FFF3E0',     # Light orange background
        'error': '#F44336',             # Red for errors
        'error_light': '#FFEBEE',       # Light red background
        'info': '#2196F3',              # Blue for info
        'info_light': '#E3F2FD',        # Light blue background
        
        # Neutral colors
        'background': '#FAFAFA',        # Light gray background
        'surface': '#FFFFFF',           # White surface
        'surface_variant': '#F5F5F5',   # Light gray variant
        'outline': '#E0E0E0',           # Border color
        'text_primary': '#212121',      # Dark text
        'text_secondary': '#757575',    # Secondary text
        'text_hint': '#9E9E9E',         # Hint text
    }
    
    # Typography
    FONTS = {
        'title': ('Segoe UI', 18, 'bold'),
        'heading': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'body_bold': ('Segoe UI', 10, 'bold'),
        'small': ('Segoe UI', 9),
        'small_bold': ('Segoe UI', 9, 'bold'),
    }
    
    # Spacing
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
    }
    
    # Component dimensions
    DIMENSIONS = {
        'button_height': 32,
        'input_height': 28,
        'card_padding': 16,
        'border_radius': 4,
    }
    
    @classmethod
    def configure_styles(cls, root: tk.Tk) -> ttk.Style:
        """
        Configure TTK styles for professional appearance.
        
        Args:
            root: The root Tk window
            
        Returns:
            Configured TTK Style object
        """
        style = ttk.Style()
        
        # Configure root window
        root.configure(bg=cls.COLORS['background'])
        
        # Configure main styles
        cls._configure_frame_styles(style)
        cls._configure_button_styles(style)
        cls._configure_label_styles(style)
        cls._configure_notebook_styles(style)
        cls._configure_treeview_styles(style)
        
        return style
    
    @classmethod
    def _configure_frame_styles(cls, style: ttk.Style):
        """Configure frame styles."""
        # Main frame
        style.configure(
            'Main.TFrame',
            background=cls.COLORS['background'],
            relief='flat'
        )
        
        # Card frame - elevated appearance
        style.configure(
            'Card.TFrame',
            background=cls.COLORS['surface'],
            relief='raised',
            borderwidth=1
        )
        
        # Surface frame
        style.configure(
            'Surface.TFrame',
            background=cls.COLORS['surface'],
            relief='flat'
        )
        
        # Header frame
        style.configure(
            'Header.TFrame',
            background=cls.COLORS['primary'],
            relief='flat'
        )
    
    @classmethod
    def _configure_button_styles(cls, style: ttk.Style):
        """Configure button styles."""
        # Primary button
        style.configure(
            'Primary.TButton',
            background=cls.COLORS['primary'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            font=cls.FONTS['body_bold']
        )
        style.map(
            'Primary.TButton',
            background=[('active', cls.COLORS['primary_dark']),
                       ('pressed', cls.COLORS['primary_dark'])]
        )
        
        # Accent button
        style.configure(
            'Accent.TButton',
            background=cls.COLORS['accent'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            font=cls.FONTS['body_bold']
        )
        style.map(
            'Accent.TButton',
            background=[('active', '#E8800D'),
                       ('pressed', '#E8800D')]
        )
        
        # Success button
        style.configure(
            'Success.TButton',
            background=cls.COLORS['success'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            font=cls.FONTS['body_bold']
        )
    
    @classmethod
    def _configure_label_styles(cls, style: ttk.Style):
        """Configure label styles."""
        # Title label
        style.configure(
            'Title.TLabel',
            background=cls.COLORS['background'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['title']
        )
        
        # Heading label
        style.configure(
            'Heading.TLabel',
            background=cls.COLORS['background'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['heading']
        )
        
        # Body label
        style.configure(
            'Body.TLabel',
            background=cls.COLORS['background'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['body']
        )
        
        # Secondary label
        style.configure(
            'Secondary.TLabel',
            background=cls.COLORS['background'],
            foreground=cls.COLORS['text_secondary'],
            font=cls.FONTS['body']
        )
        
        # Success label
        style.configure(
            'Success.TLabel',
            background=cls.COLORS['background'],
            foreground=cls.COLORS['success'],
            font=cls.FONTS['body_bold']
        )
        
        # Warning label
        style.configure(
            'Warning.TLabel',
            background=cls.COLORS['background'],
            foreground=cls.COLORS['warning'],
            font=cls.FONTS['body_bold']
        )
        
        # Error label
        style.configure(
            'Error.TLabel',
            background=cls.COLORS['background'],
            foreground=cls.COLORS['error'],
            font=cls.FONTS['body_bold']
        )
        
        # Card labels (on white background)
        style.configure(
            'Card.TLabel',
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['body']
        )
        
        style.configure(
            'CardHeading.TLabel',
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['heading']
        )
    
    @classmethod
    def _configure_notebook_styles(cls, style: ttk.Style):
        """Configure notebook (tabs) styles."""
        style.configure(
            'Professional.TNotebook',
            background=cls.COLORS['background'],
            borderwidth=0
        )
        
        style.configure(
            'Professional.TNotebook.Tab',
            background=cls.COLORS['surface_variant'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['body_bold'],
            padding=[12, 8],
            borderwidth=1,
            relief='raised'
        )
        
        style.map(
            'Professional.TNotebook.Tab',
            background=[('selected', cls.COLORS['surface']),
                       ('active', cls.COLORS['primary_light'])],
            foreground=[('selected', cls.COLORS['primary']),
                       ('active', 'white')]
        )
    
    @classmethod
    def _configure_treeview_styles(cls, style: ttk.Style):
        """Configure treeview styles for data tables."""
        style.configure(
            'Professional.Treeview',
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            fieldbackground=cls.COLORS['surface'],
            font=cls.FONTS['body'],
            borderwidth=1
        )
        
        style.configure(
            'Professional.Treeview.Heading',
            background=cls.COLORS['primary'],
            foreground='white',
            font=cls.FONTS['body_bold'],
            relief='flat'
        )
        
        style.map(
            'Professional.Treeview',
            background=[('selected', cls.COLORS['primary_light'])],
            foreground=[('selected', 'white')]
        )
    
    @classmethod
    def get_icon(cls, icon_type: str) -> str:
        """
        Get icon/emoji for different UI elements.
        
        Args:
            icon_type: Type of icon needed
            
        Returns:
            Unicode icon/emoji character
        """
        icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'file': '📄',
            'folder': '📁',
            'match': '🎯',
            'money': '💰',
            'stats': '📊',
            'invoice': '🧾',
            'transaction': '💳',
            'search': '🔍',
            'checkmark': '✓',
            'cross': '✗',
        }
        return icons.get(icon_type, '•')
    
    @classmethod
    def create_card_frame(cls, parent: tk.Widget, **kwargs) -> ttk.Frame:
        """
        Create a styled card frame.
        
        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
            
        Returns:
            Configured card frame
        """
        frame = ttk.Frame(parent, style='Card.TFrame', **kwargs)
        frame.configure(padding=cls.SPACING['md'])
        return frame
    
    @classmethod
    def create_metric_card(cls, parent: tk.Widget, title: str, value: str, 
                          icon: str = '', color: str = 'text_primary') -> ttk.Frame:
        """
        Create a metric display card.
        
        Args:
            parent: Parent widget
            title: Card title
            value: Main value to display
            icon: Icon to show
            color: Color scheme key
            
        Returns:
            Configured metric card frame
        """
        card = cls.create_card_frame(parent)
        
        # Icon and title row
        header_frame = ttk.Frame(card, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, cls.SPACING['sm']))
        
        if icon:
            icon_label = ttk.Label(header_frame, text=icon, 
                                  style='Card.TLabel', font=cls.FONTS['heading'])
            icon_label.pack(side=tk.LEFT, padx=(0, cls.SPACING['xs']))
        
        title_label = ttk.Label(header_frame, text=title, 
                               style='Card.TLabel', font=cls.FONTS['small_bold'])
        title_label.pack(side=tk.LEFT)
        
        # Value
        value_label = ttk.Label(card, text=value, 
                               style='Card.TLabel', font=cls.FONTS['title'])
        value_label.pack()
        
        return card