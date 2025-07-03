"""
MT940 file generator for creating upload-ready files from matched transactions.
"""

import os
from decimal import Decimal
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from .models import Transaction, MatchResult
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.logging_setup import LoggingSetup


class MT940Generator:
    """Generates MT940 files from matched transaction data for SnelStart upload."""
    
    def __init__(self):
        """Initialize the MT940 generator."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        
    def generate_from_matches(self, matched_pairs: List[MatchResult], output_path: str) -> str:
        """
        Generate MT940 file containing only matched transactions.
        
        Args:
            matched_pairs: List of matched transaction-invoice pairs
            output_path: Path where to save the generated MT940 file
            
        Returns:
            Path to the generated MT940 file
            
        Raises:
            ValueError: If no matched pairs provided
            IOError: If file cannot be written
        """
        if not matched_pairs:
            raise ValueError("No matched pairs provided for MT940 generation")
            
        self.logger.info(f"Generating MT940 file with {len(matched_pairs)} matched transactions")
        
        # Extract transactions from matched pairs
        matched_transactions = [match.transaction for match in matched_pairs]
        
        # Sort transactions by date for proper MT940 ordering
        sorted_transactions = sorted(matched_transactions, key=lambda t: t.date)
        
        # Generate MT940 content
        mt940_content = self._build_mt940_content(sorted_transactions)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(mt940_content)
            
            self.logger.info(f"Successfully generated MT940 file: {output_path}")
            return output_path
            
        except IOError as e:
            self.logger.error(f"Failed to write MT940 file: {e}")
            raise
            
    def _build_mt940_content(self, transactions: List[Transaction]) -> str:
        """
        Build complete MT940 file content from transactions.
        
        Args:
            transactions: Sorted list of transactions
            
        Returns:
            Complete MT940 file content as string
        """
        lines = []
        
        # Header section
        lines.extend(self._generate_header())
        
        # Calculate balances
        opening_balance, closing_balance = self._calculate_balances(transactions)
        
        # Opening balance
        lines.append(f":60F:{opening_balance}")
        
        # Transaction lines
        for transaction in transactions:
            lines.extend(self._generate_transaction_lines(transaction))
        
        # Closing balance
        lines.append(f":62F:{closing_balance}")
        
        return '\n'.join(lines)
        
    def _generate_header(self) -> List[str]:
        """
        Generate MT940 header lines.
        
        Returns:
            List of header lines
        """
        # Use generic header based on sample format
        return [
            "ABNANL2A",
            "940", 
            "ABNANL2A",
            ":20:MATCHED TRANSACTIONS",
            ":25:438661141",
            f":28:{datetime.now().strftime('%y%m')}/1"
        ]
        
    def _generate_transaction_lines(self, transaction: Transaction) -> List[str]:
        """
        Generate :61: and :86: lines for a single transaction.
        
        Args:
            transaction: Transaction to convert to MT940 format
            
        Returns:
            List containing transaction and detail lines
        """
        # :61: line - Transaction summary
        date_str = transaction.date.strftime('%y%m%d')
        amount_abs = abs(transaction.amount)
        debit_credit = 'D' if transaction.amount < 0 else 'C'
        
        # Format amount with proper decimal places
        amount_str = f"{amount_abs:.2f}".replace('.', ',')
        
        # Use transaction reference or generate one
        ref_str = transaction.reference if transaction.reference else "NONREF"
        
        transaction_line = f":61:{date_str}{date_str}{debit_credit}{amount_str}N249{ref_str}"
        
        # :86: line - Transaction details with SEPA fields
        detail_line = self._generate_detail_line(transaction)
        
        return [transaction_line, detail_line]
        
    def _generate_detail_line(self, transaction: Transaction) -> str:
        """
        Generate :86: detail line with SEPA fields.
        
        Args:
            transaction: Transaction with SEPA information
            
        Returns:
            Formatted :86: detail line
        """
        parts = [":86:/TRTP/SEPA INCASSO BEDRIJVEN DOORLOPEND"]
        
        # Add SEPA fields if available
        if transaction.counterparty_name:
            parts.append(f"/NAME/{transaction.counterparty_name}")
            
        if transaction.remittance_info:
            parts.append(f"/REMI/{transaction.remittance_info}")
            
        if transaction.counterparty_iban:
            parts.append(f"/IBAN/{transaction.counterparty_iban}")
            
        # Add reference if available
        if transaction.reference:
            parts.append(f"/EREF/{transaction.reference}")
            
        return ''.join(parts)
        
    def _calculate_balances(self, transactions: List[Transaction]) -> tuple[str, str]:
        """
        Calculate opening and closing balances for the MT940 file.
        
        Args:
            transactions: List of transactions
            
        Returns:
            Tuple of (opening_balance, closing_balance) as formatted strings
        """
        if not transactions:
            # Default balances if no transactions
            return "C991231EUR0,00", "C991231EUR0,00"
            
        # Use the first transaction date for balance dates
        first_date = transactions[0].date
        balance_date = first_date.strftime('%y%m%d')
        
        # Calculate total transaction amount
        total_amount = sum(t.amount for t in transactions)
        
        # For simplicity, start with 0 opening balance
        # In a real scenario, this might be retrieved from the original MT940
        opening_amount = Decimal('0.00')
        closing_amount = opening_amount + total_amount
        
        # Format balances
        opening_balance = self._format_balance(balance_date, opening_amount)
        closing_balance = self._format_balance(balance_date, abs(closing_amount), closing_amount < 0)
        
        return opening_balance, closing_balance
        
    def _format_balance(self, date_str: str, amount: Decimal, is_debit: bool = False) -> str:
        """
        Format balance in MT940 format.
        
        Args:
            date_str: Date in YYMMDD format
            amount: Balance amount
            is_debit: True if balance is debit, False if credit
            
        Returns:
            Formatted balance string
        """
        debit_credit = 'D' if is_debit else 'C'
        amount_str = f"{amount:.2f}".replace('.', ',')
        
        return f"{debit_credit}{date_str}EUR{amount_str}"