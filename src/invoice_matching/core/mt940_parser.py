"""
Simple MT940 parser using the mt-940 package.
"""

from decimal import Decimal
from typing import List
from pathlib import Path
import mt940

from .models import Transaction
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.logging_setup import LoggingSetup


class MT940Parser:
    """Simple parser for MT940 bank statement files using mt-940 package."""
    
    def __init__(self, file_path: str):
        """
        Initialize MT940 parser.
        
        Args:
            file_path: Path to MT940 file
        """
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.file_path = Path(file_path)
        self.logger.debug(f"Initialized MT940 parser for file: {file_path}")
    
    def parse(self) -> List[Transaction]:
        """
        Parse MT940 file and return list of transactions.
        
        Returns:
            List of Transaction objects
        """
        self.logger.info(f"Starting MT940 parsing for file: {self.file_path}")
        
        if not self.file_path.exists():
            self.logger.error(f"MT940 file not found: {self.file_path}")
            raise FileNotFoundError(f"MT940 file not found: {self.file_path}")
        
        transactions = []
        
        # Parse MT940 file using mt940 package
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                statements = mt940.parse(file)
            self.logger.debug(f"Successfully parsed MT940 file, found {len(list(statements))} statements")
        except Exception as e:
            self.logger.error(f"Failed to parse MT940 file: {e}")
            raise
        
        # Re-parse for processing (statements is consumed after iteration)
        with open(self.file_path, 'r', encoding='utf-8') as file:
            statements = mt940.parse(file)
        
        # Convert mt940 transactions to our Transaction objects
        for statement in statements:
            self.logger.debug(f"Processing statement with {len(statement.transactions)} transactions")
            for mt940_transaction in statement.transactions:
                transaction = self._convert_mt940_transaction(mt940_transaction)
                if transaction:
                    transactions.append(transaction)
        
        self.logger.info(f"MT940 parsing complete: {len(transactions)} transactions extracted")
        return transactions
    
    def _convert_mt940_transaction(self, mt940_transaction) -> Transaction:
        """Convert mt940 transaction to our Transaction object."""
        try:
            # Extract basic information
            amount = Decimal(str(mt940_transaction.data['amount'].amount))
            date = mt940_transaction.data['date']
            
            # Get reference (transaction reference or generate one)
            reference = getattr(mt940_transaction.data.get('transaction_reference'), 'data', None)
            if not reference:
                reference = f"TXN_{date.strftime('%Y%m%d')}_{abs(hash(str(mt940_transaction)))%10000:04d}"
            
            # Get description from various possible fields
            description_parts = []
            
            # Add transaction details if available
            details = mt940_transaction.data.get('transaction_details', '')
            if details:
                description_parts.append(str(details))
            
            # Add purpose if available
            purpose = mt940_transaction.data.get('purpose', '')
            if purpose:
                description_parts.append(str(purpose))
            
            # Add extra details if available
            extra_details = mt940_transaction.data.get('extra_details', '')
            if extra_details:
                description_parts.append(str(extra_details))
            
            # Combine description parts
            description = ' '.join(description_parts).strip()
            if not description:
                description = f"Transaction {reference}"
            
            # Get account if available
            account = getattr(mt940_transaction.data.get('account_identification'), 'data', None)
            
            return Transaction(
                amount=amount,
                description=description,
                date=date,
                reference=str(reference),
                account=str(account) if account else None
            )
            
        except Exception as e:
            self.logger.warning(f"Error converting MT940 transaction: {e}")
            return None


def parse_mt940_file(file_path: str) -> List[Transaction]:
    """
    Convenience function to parse MT940 file using mt-940 package.
    
    Args:
        file_path: Path to MT940 file
        
    Returns:
        List of Transaction objects
    """
    parser = MT940Parser(file_path)
    return parser.parse()