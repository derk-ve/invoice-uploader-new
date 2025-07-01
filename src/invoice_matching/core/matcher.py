"""
Simple invoice matching logic.
"""

from decimal import Decimal
from typing import List, Optional

from .models import Transaction, Invoice, MatchResult, MatchingSummary
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.logging_setup import LoggingSetup


class InvoiceMatcher:
    """Simple class for matching transactions to invoices."""
    
    def __init__(self):
        """Initialize matcher."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
    
    def match_transactions_to_invoices(
        self, 
        transactions: List[Transaction], 
        invoices: List[Invoice]
    ) -> MatchingSummary:
        """
        Match transactions to invoices based on invoice number in description.
        
        Args:
            transactions: List of bank transactions
            invoices: List of invoices (from PDF filenames)
            
        Returns:
            MatchingSummary with results
        """
        self.logger.info(f"Starting invoice matching: {len(transactions)} transactions vs {len(invoices)} invoices")
        
        matched_pairs = []
        unmatched_transactions = []
        used_invoices = set()
        
        for transaction in transactions:
            # Try to find matching invoice
            match_found = False
            
            for i, invoice in enumerate(invoices):
                if i in used_invoices:
                    continue
                
                # Check if invoice number appears in transaction description
                if invoice.invoice_number.lower() in transaction.description.lower():
                    # Create match
                    match = MatchResult(
                        transaction=transaction,
                        invoice=invoice,
                        confidence_score=1.0,
                        amount_difference=Decimal('0'),
                        match_reasons=[f"Found '{invoice.invoice_number}' in description"]
                    )
                    matched_pairs.append(match)
                    used_invoices.add(i)
                    match_found = True
                    self.logger.debug(f"Matched transaction {transaction.reference} with invoice {invoice.invoice_number}")
                    break
            
            if not match_found:
                unmatched_transactions.append(transaction)
        
        # Collect unmatched invoices
        unmatched_invoices = [
            invoice for i, invoice in enumerate(invoices)
            if i not in used_invoices
        ]
        
        # Calculate stats
        total_transactions = len(transactions)
        match_rate = (len(matched_pairs) / total_transactions * 100) if total_transactions > 0 else 0.0
        total_matched_amount = sum(pair.transaction.amount for pair in matched_pairs)
        
        self.logger.info(f"Matching complete: {len(matched_pairs)} matches, {len(unmatched_transactions)} unmatched transactions, {match_rate:.1f}% match rate")
        
        return MatchingSummary(
            matched_pairs=matched_pairs,
            unmatched_transactions=unmatched_transactions,
            unmatched_invoices=unmatched_invoices,
            total_transactions=total_transactions,
            total_invoices=len(invoices),
            match_rate=match_rate,
            total_matched_amount=total_matched_amount
        )


def do_bookkeeping(
    transactions: List[Transaction], 
    invoices: List[Invoice]
) -> MatchingSummary:
    """
    Simple entry point for invoice matching.
    
    Args:
        transactions: List of transactions from MT940
        invoices: List of invoices from PDF files
        
    Returns:
        MatchingSummary with results
    """
    matcher = InvoiceMatcher()
    return matcher.match_transactions_to_invoices(transactions, invoices)