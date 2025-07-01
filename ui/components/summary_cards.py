"""
Summary cards component for displaying matching metrics and statistics.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from decimal import Decimal

from ..styles.theme import AppTheme
from src.invoice_matching.core.models import MatchingSummary


class SummaryCards:
    """Component for displaying matching summary in visual metric cards."""
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize summary cards component.
        
        Args:
            parent: Parent widget to attach this component to
        """
        self.parent = parent
        self.cards_frame: Optional[ttk.Frame] = None
        
    def setup_ui(self, row_start: int = 0) -> int:
        """
        Create the summary cards UI elements.
        
        Args:
            row_start: Starting row for grid layout
            
        Returns:
            Next available row number
        """
        current_row = row_start
        
        # Section title
        title_label = ttk.Label(
            self.parent, 
            text="📊 Matching Summary", 
            style='Heading.TLabel'
        )
        title_label.grid(row=current_row, column=0, columnspan=4, 
                        sticky=(tk.W, tk.N), pady=(0, AppTheme.SPACING['md']))
        current_row += 1
        
        # Cards container frame
        self.cards_frame = ttk.Frame(self.parent, style='Main.TFrame')
        self.cards_frame.grid(row=current_row, column=0, columnspan=4, 
                             sticky=(tk.W, tk.E), pady=(0, AppTheme.SPACING['lg']))
        
        # Configure grid weights for responsive layout
        for i in range(4):
            self.cards_frame.columnconfigure(i, weight=1)
            
        # Show initial empty state
        self._show_empty_state()
        
        return current_row + 1
    
    def _show_empty_state(self):
        """Show empty state when no results are available."""
        self._clear_cards()
        
        empty_label = ttk.Label(
            self.cards_frame,
            text="📋 Run matching to see summary statistics",
            style='Secondary.TLabel'
        )
        empty_label.grid(row=0, column=0, columnspan=4, pady=AppTheme.SPACING['md'])
    
    def _clear_cards(self):
        """Clear all cards from the display."""
        if self.cards_frame:
            for widget in self.cards_frame.winfo_children():
                widget.destroy()
    
    def show_summary(self, summary: MatchingSummary):
        """
        Display matching summary in metric cards.
        
        Args:
            summary: Matching summary data to display
        """
        self._clear_cards()
        
        # Calculate additional metrics
        total_processed = summary.total_transactions + summary.total_invoices
        success_rate = (len(summary.matched_pairs) / max(summary.total_transactions, 1)) * 100
        
        # Card data configuration
        cards_data = [
            {
                'title': 'Matched Pairs',
                'value': str(len(summary.matched_pairs)),
                'icon': AppTheme.get_icon('match'),
                'color': 'success' if len(summary.matched_pairs) > 0 else 'text_secondary'
            },
            {
                'title': 'Success Rate',
                'value': f"{success_rate:.1f}%",
                'icon': AppTheme.get_icon('stats'),
                'color': 'success' if success_rate >= 50 else 'warning' if success_rate >= 25 else 'error'
            },
            {
                'title': 'Total Amount',
                'value': f"€{summary.total_matched_amount:,.2f}",
                'icon': AppTheme.get_icon('money'),
                'color': 'primary'
            },
            {
                'title': 'Unmatched Items',
                'value': str(len(summary.unmatched_transactions) + len(summary.unmatched_invoices)),
                'icon': AppTheme.get_icon('warning'),
                'color': 'warning' if (len(summary.unmatched_transactions) + len(summary.unmatched_invoices)) > 0 else 'success'
            }
        ]
        
        # Create metric cards
        for i, card_data in enumerate(cards_data):
            self._create_metric_card(
                column=i,
                title=card_data['title'],
                value=card_data['value'],
                icon=card_data['icon'],
                color=card_data['color']
            )
    
    def _create_metric_card(self, column: int, title: str, value: str, 
                           icon: str, color: str):
        """
        Create an individual metric card.
        
        Args:
            column: Grid column position
            title: Card title
            value: Main value to display
            icon: Icon character
            color: Color theme key
        """
        # Card frame
        card = AppTheme.create_card_frame(self.cards_frame)
        card.grid(row=0, column=column, padx=AppTheme.SPACING['sm'], 
                 pady=AppTheme.SPACING['sm'], sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Icon and title container
        header_frame = ttk.Frame(card, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, AppTheme.SPACING['sm']))
        
        # Icon
        icon_label = ttk.Label(
            header_frame, 
            text=icon, 
            style='Card.TLabel',
            font=('Segoe UI', 16)
        )
        icon_label.pack(side=tk.LEFT, padx=(0, AppTheme.SPACING['xs']))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text=title,
            style='Card.TLabel',
            font=AppTheme.FONTS['small_bold']
        )
        title_label.pack(side=tk.LEFT)
        
        # Value
        value_label = ttk.Label(
            card,
            text=value,
            style='Card.TLabel',
            font=AppTheme.FONTS['title']
        )
        value_label.pack()
        
        # Apply color styling based on the color theme
        self._apply_card_color(value_label, color)
    
    def _apply_card_color(self, label: ttk.Label, color: str):
        """
        Apply color styling to a card value label.
        
        Args:
            label: Label widget to color
            color: Color theme key
        """
        color_map = {
            'success': AppTheme.COLORS['success'],
            'warning': AppTheme.COLORS['warning'],
            'error': AppTheme.COLORS['error'],
            'primary': AppTheme.COLORS['primary'],
            'text_secondary': AppTheme.COLORS['text_secondary']
        }
        
        fg_color = color_map.get(color, AppTheme.COLORS['text_primary'])
        label.configure(foreground=fg_color)
    
    def show_processing(self):
        """Show processing state in summary cards."""
        self._clear_cards()
        
        processing_label = ttk.Label(
            self.cards_frame,
            text="🔄 Processing matching results...",
            style='Secondary.TLabel'
        )
        processing_label.grid(row=0, column=0, columnspan=4, pady=AppTheme.SPACING['md'])
    
    def show_error(self, error_message: str):
        """
        Show error state in summary cards.
        
        Args:
            error_message: Error message to display
        """
        self._clear_cards()
        
        error_label = ttk.Label(
            self.cards_frame,
            text=f"❌ Error: {error_message}",
            style='Error.TLabel'
        )
        error_label.grid(row=0, column=0, columnspan=4, pady=AppTheme.SPACING['md'])