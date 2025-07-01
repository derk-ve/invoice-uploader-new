"""
Data models for invoice matching system.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import List, Optional


@dataclass
class Transaction:
    """
    Represents a bank transaction from MT940 format.
    
    Attributes:
        amount: Transaction amount (positive for credit, negative for debit)
        description: Transaction description/reference text
        date: Transaction date
        reference: Bank reference number
        account: Bank account number (optional)
    """
    amount: Decimal
    description: str
    date: datetime
    reference: str
    account: Optional[str] = None
    
    def __post_init__(self):
        """Validate transaction data after initialization."""
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))
        
        if not self.description:
            raise ValueError("Transaction description cannot be empty")
        
        if not self.reference:
            raise ValueError("Transaction reference cannot be empty")


@dataclass
class Invoice:
    """
    Represents an invoice to be matched with transactions.
    
    Attributes:
        invoice_number: Unique invoice identifier (extracted from filename)
        file_path: Path to the PDF invoice file
        amount: Invoice amount (optional, may be extracted later)
        date: Invoice date (optional, may be extracted later)
        description: Invoice description (optional)
        vendor: Vendor name (optional)
    """
    invoice_number: str
    file_path: str
    amount: Optional[Decimal] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    
    def __post_init__(self):
        """Validate invoice data after initialization."""
        if self.amount is not None:
            if not isinstance(self.amount, Decimal):
                self.amount = Decimal(str(self.amount))
            
            if self.amount <= 0:
                raise ValueError("Invoice amount must be positive")
        
        if not self.invoice_number:
            raise ValueError("Invoice number cannot be empty")
        
        if not self.file_path:
            raise ValueError("File path cannot be empty")


@dataclass
class MatchResult:
    """
    Represents a successful match between a transaction and invoice.
    
    Attributes:
        transaction: The matched transaction
        invoice: The matched invoice
        confidence_score: Matching confidence (0.0 to 1.0)
        amount_difference: Absolute difference between amounts
        match_reasons: List of reasons why this match was made
    """
    transaction: Transaction
    invoice: Invoice
    confidence_score: float
    amount_difference: Decimal
    match_reasons: List[str]
    
    def __post_init__(self):
        """Validate match result data after initialization."""
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        
        if not isinstance(self.amount_difference, Decimal):
            self.amount_difference = Decimal(str(self.amount_difference))
        
        if self.amount_difference < 0:
            raise ValueError("Amount difference must be non-negative")


@dataclass
class MatchingSummary:
    """
    Summary of matching results.
    
    Attributes:
        matched_pairs: List of successful matches
        unmatched_transactions: List of transactions that couldn't be matched
        unmatched_invoices: List of invoices that couldn't be matched
        total_transactions: Total number of input transactions
        total_invoices: Total number of input invoices
        match_rate: Percentage of transactions that were matched
        total_matched_amount: Sum of amounts from matched transactions
    """
    matched_pairs: List[MatchResult]
    unmatched_transactions: List[Transaction]
    unmatched_invoices: List[Invoice]
    total_transactions: int
    total_invoices: int
    match_rate: float
    total_matched_amount: Decimal
    
    def __post_init__(self):
        """Calculate derived statistics after initialization."""
        if not isinstance(self.total_matched_amount, Decimal):
            self.total_matched_amount = Decimal(str(self.total_matched_amount))
        
        # Validate that counts are consistent
        expected_unmatched = self.total_transactions - len(self.matched_pairs)
        if len(self.unmatched_transactions) != expected_unmatched:
            raise ValueError("Unmatched transactions count doesn't match expected value")
    
    @property
    def matched_count(self) -> int:
        """Number of successful matches."""
        return len(self.matched_pairs)
    
    @property
    def unmatched_count(self) -> int:
        """Number of unmatched transactions."""
        return len(self.unmatched_transactions)
    
    @property
    def unmatched_invoices_count(self) -> int:
        """Number of unmatched invoices."""
        return len(self.unmatched_invoices)