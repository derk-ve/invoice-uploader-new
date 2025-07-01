"""
Transaction filtering for MT940 transactions based on configured criteria.
"""

import re
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
        self.sip_pattern = re.compile(self.config.get('sip_pattern', r'SIP\d{7,9}'), re.IGNORECASE)
        self.require_both = self.config.get('require_both', True)
        self.case_sensitive = self.config.get('case_sensitive', False)
        
        self.logger.info(f"Transaction filtering {'enabled' if self.enabled else 'disabled'}")
    
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
        
        # Check for ROYAL CANIN in counterparty name or description
        has_royal_canin = self._has_royal_canin(transaction)
        
        # Check for SIP invoice number in remittance info or description
        has_sip_number = self._has_sip_number(transaction)
        
        if self.require_both:
            result = has_royal_canin and has_sip_number
        else:
            result = has_royal_canin or has_sip_number
        
        if not result:
            self.logger.debug(f"Filtered out transaction {transaction.reference}: "
                            f"Royal Canin={has_royal_canin}, SIP={has_sip_number}")
        
        return result
    
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
    
    def _has_sip_number(self, transaction: Transaction) -> bool:
        """Check if transaction contains SIP invoice number."""
        # Check remittance info first (more reliable)
        if transaction.remittance_info and self.sip_pattern.search(transaction.remittance_info):
            return True
        
        # Fallback to description
        if self.sip_pattern.search(transaction.description):
            return True
        
        return False