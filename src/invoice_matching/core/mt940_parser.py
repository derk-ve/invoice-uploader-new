"""
Enhanced MT940 parser with SEPA field extraction and filtering.
"""

import re
from decimal import Decimal
from typing import List, Optional, Dict
from pathlib import Path
import mt940

from .models import Transaction
from .transaction_filter import TransactionFilter
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.logging_setup import LoggingSetup
from utils.config import Config


class MT940Parser:
    """Enhanced parser for MT940 bank statement files with SEPA field extraction and filtering."""
    
    def __init__(self, file_path: str):
        """
        Initialize MT940 parser.
        
        Args:
            file_path: Path to MT940 file
        """
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.file_path = Path(file_path)
        self.filter = TransactionFilter()
        self.logger.debug(f"Initialized enhanced MT940 parser for file: {file_path}")
    
    def parse(self) -> List[Transaction]:
        """
        Parse MT940 file and return filtered list of transactions.
        
        Returns:
            List of filtered Transaction objects
        """
        self.logger.info(f"Starting enhanced MT940 parsing for file: {self.file_path}")
        
        if not self.file_path.exists():
            self.logger.error(f"MT940 file not found: {self.file_path}")
            raise FileNotFoundError(f"MT940 file not found: {self.file_path}")
        
        all_transactions = []
        unique_transactions = set()  # For deduplication
        filtered_transactions = []
        
        # Parse MT940 file using mt940 package (single read)
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                statements = list(mt940.parse(file))  # Convert to list to reuse
            self.logger.debug(f"Successfully parsed MT940 file, found {len(statements)} statements")
        except Exception as e:
            self.logger.error(f"Failed to parse MT940 file: {e}")
            raise
        
        # Convert mt940 transactions to our Transaction objects with deduplication
        total_raw_transactions = 0
        duplicates_found = 0
        
        for statement_idx, statement in enumerate(statements):
            statement_transactions = len(statement.transactions)
            total_raw_transactions += statement_transactions
            self.logger.debug(f"Processing statement {statement_idx + 1}/{len(statements)} with {statement_transactions} transactions")
            
            for mt940_transaction in statement.transactions:
                transaction = self._convert_mt940_transaction(mt940_transaction)
                if transaction:
                    # Create unique key for deduplication (date + amount + reference)
                    unique_key = f"{transaction.date.strftime('%Y-%m-%d')}_{transaction.amount}_{transaction.reference}"
                    
                    if unique_key not in unique_transactions:
                        unique_transactions.add(unique_key)
                        all_transactions.append(transaction)
                        
                        # Apply filtering
                        if self.filter.should_include_transaction(transaction):
                            filtered_transactions.append(transaction)
                    else:
                        duplicates_found += 1
                        # self.logger.debug(f"Duplicate transaction found and skipped: {unique_key}")
        
        self.logger.info(f"MT940 parsing complete: {len(statements)} total statements, "
                        f"{total_raw_transactions} raw transactions, "
                        f"{len(all_transactions)} unique transactions ({duplicates_found} duplicate transactions removed), "
                        f"{len(filtered_transactions)} after filtering ({len(all_transactions) - len(filtered_transactions)} filtered out)")
        return filtered_transactions
    
    def _convert_mt940_transaction(self, mt940_transaction) -> Optional[Transaction]:
        """Convert mt940 transaction to our Transaction object with SEPA field extraction."""
        try:
            # Extract basic information
            amount = Decimal(str(mt940_transaction.data['amount'].amount))
            date = mt940_transaction.data['date']
            
            # Get reference (transaction reference or generate one)
            reference = getattr(mt940_transaction.data.get('transaction_reference'), 'data', None)
            if not reference:
                reference = f"TXN_{date.strftime('%Y%m%d')}_{abs(hash(str(mt940_transaction)))%10000:04d}"
            
            # Get account if available
            account = getattr(mt940_transaction.data.get('account_identification'), 'data', None)
            
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
            
            # Extract SEPA structured fields from description
            sepa_fields = self._extract_sepa_fields(description)
            
            return Transaction(
                amount=amount,
                description=description,
                date=date,
                reference=str(reference),
                account=str(account) if account else None,
                counterparty_name=sepa_fields.get('name'),
                remittance_info=sepa_fields.get('remittance'),
                counterparty_iban=sepa_fields.get('iban')
            )
            
        except Exception as e:
            self.logger.warning(f"Error converting MT940 transaction: {e}")
            return None
    
    def _extract_sepa_fields(self, description: str) -> Dict[str, Optional[str]]:
        """
        Extract structured SEPA fields from transaction description.
        
        Args:
            description: Transaction description containing SEPA fields
            
        Returns:
            Dictionary with extracted fields: name, remittance, iban
        """
        sepa_fields = {
            'name': None,
            'remittance': None,
            'iban': None
        }
        
        # SEPA fields are typically in format /FIELD/VALUE/
        # Extract NAME field (counterparty name)
        name_match = re.search(r'/NAME/([^/]+)/', description)
        if name_match:
            sepa_fields['name'] = name_match.group(1).strip()
        
        # Extract REMI field (remittance information - often contains invoice numbers)
        remi_match = re.search(r'/REMI/([^/]+)/', description)
        if remi_match:
            sepa_fields['remittance'] = remi_match.group(1).strip()
        
        # Extract IBAN field (counterparty IBAN)
        iban_match = re.search(r'/IBAN/([^/]+)/', description)
        if iban_match:
            sepa_fields['iban'] = iban_match.group(1).strip()
        
        # Log extracted fields for debugging
        # if any(sepa_fields.values()):
            # self.logger.debug(f"Extracted SEPA fields: {sepa_fields}")
        
        return sepa_fields


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