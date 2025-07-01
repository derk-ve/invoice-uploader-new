"""
Transaction filtering for MT940 transactions based on configured criteria.
"""

from typing import Optional

from .models import Transaction
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.logging_setup import LoggingSetup
from utils.config import Config


class TransactionFilter:
    """Handles filtering of transactions based on configured criteria."""
    
    def __init__(self):
        """Initialize transaction filter with configuration."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.config = Config.get_timing_config('transaction_filtering')
        
        self.enabled = self.config.get('enabled', True)
        self.royal_canin_keywords = self.config.get('royal_canin_keywords', ['ROYAL CANIN'])
        self.case_sensitive = self.config.get('case_sensitive', False)
        
        self.logger.info(f"Royal Canin transaction filtering {'enabled' if self.enabled else 'disabled'}")
    
    def should_include_transaction(self, transaction: Transaction) -> bool:
        """
        Determine if transaction should be included based on filtering criteria.
        
        Args:
            transaction: Transaction to evaluate
            
        Returns:
            True if transaction should be included, False otherwise
        """
        if not self.enabled:
            return True
        
        # Only check for ROYAL CANIN in counterparty name or description
        has_royal_canin = self._has_royal_canin(transaction)
        
        if not has_royal_canin:
            self.logger.debug(f"Filtered out non-Royal Canin transaction: {transaction.date}: {transaction.counterparty_name}: {transaction.amount}")
        
        return has_royal_canin
    
    def _has_royal_canin(self, transaction: Transaction) -> bool:
        """Check if transaction is related to ROYAL CANIN."""
        # Check counterparty name first (more reliable)
        if transaction.counterparty_name:
            text = transaction.counterparty_name if self.case_sensitive else transaction.counterparty_name.upper()
            for keyword in self.royal_canin_keywords:
                check_keyword = keyword if self.case_sensitive else keyword.upper()
                if check_keyword in text:
                    return True
        
        # Fallback to description
        text = transaction.description if self.case_sensitive else transaction.description.upper()
        for keyword in self.royal_canin_keywords:
            check_keyword = keyword if self.case_sensitive else keyword.upper()
            if check_keyword in text:
                return True
        
        return False
    
