#!/usr/bin/env python3
"""
Simple demo script for invoice matching using data folders.

Usage:
1. Put MT940 files in data/transactions/
2. Put PDF invoices in data/invoices/
3. Run: python3 demo.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append('src')

from invoice_matching import PDFScanner, parse_mt940_file, do_bookkeeping
from utils.logging_setup import LoggingSetup
LoggingSetup.setup_logging()
logger = LoggingSetup.get_logger(__name__)


def main():
    """Run invoice matching demo."""
    print("=== Invoice Matching Demo ===\n")
    
    # Define data directories
    transactions_dir = Path("data/transactions")
    invoices_dir = Path("data/invoices")
    
    # Check if directories exist
    if not transactions_dir.exists():
        print(f"❌ Transactions directory not found: {transactions_dir}")
        print("   Please create it and add MT940 files")
        return
    
    if not invoices_dir.exists():
        print(f"❌ Invoices directory not found: {invoices_dir}")
        print("   Please create it and add PDF invoice files")
        return
    
    # Step 1: Load transactions from MT940 files
    print("📄 Loading transactions from MT940 files...")
    transactions = []
    
    mt940_files = list(transactions_dir.glob("*.STA")) + list(transactions_dir.glob("*.MT940"))
    if not mt940_files:
        print(f"   No MT940 files found in {transactions_dir}")
        print("   Please add MT940 files (*.mt940 or *.MT940)")
        return
    
    for mt940_file in mt940_files:
        print(f"   📁 Parsing: {mt940_file.name}")
        try:
            file_transactions = parse_mt940_file(str(mt940_file))
            transactions.extend(file_transactions)
            print(f"      ✅ Found {len(file_transactions)} transactions")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    if not transactions:
        print("   No transactions loaded. Check your MT940 files.")
        return
    
    print(f"   📊 Total transactions loaded: {len(transactions)}")
    
    # Step 2: Scan for PDF invoices
    print(f"\n📁 Scanning for PDF invoices in: {invoices_dir}")
    
    try:
        scanner = PDFScanner(str(invoices_dir))
        invoices = scanner.scan()
        print(f"   📊 Found {len(invoices)} PDF invoices:")
        
        for invoice in invoices:
            print(f"      • {invoice.invoice_number} ({Path(invoice.file_path).name})")
    
    except Exception as e:
        print(f"   ❌ Error scanning invoices: {e}")
        return
    
    if not invoices:
        print("   No PDF invoices found. Add PDF files to the invoices directory.")
        return
    
    # Step 3: Match transactions to invoices
    print(f"\n🔍 Matching {len(transactions)} transactions to {len(invoices)} invoices...")
    
    try:
        summary = do_bookkeeping(transactions, invoices)
        
        # Step 4: Display results
        print(f"\n✅ Matching Results:")
        print(f"   📊 Matched pairs: {len(summary.matched_pairs)}")
        print(f"   📊 Unmatched transactions: {len(summary.unmatched_transactions)}")
        print(f"   📊 Unmatched invoices: {len(summary.unmatched_invoices)}")
        print(f"   📊 Match rate: {summary.match_rate:.1f}%")
        print(f"   💰 Total matched amount: €{summary.total_matched_amount}")
        
        # Show matched pairs
        if summary.matched_pairs:
            print(f"\n🎯 Matched Pairs:")
            for i, match in enumerate(summary.matched_pairs, 1):
                print(f"   {i}. {match.transaction.reference} ↔ {match.invoice.invoice_number}")
                print(f"      Transaction: {match.transaction.description}")
                print(f"      PDF File: {Path(match.invoice.file_path).name}")
                print(f"      Amount: €{match.transaction.amount}")
                print()
        
        # # Show unmatched transactions
        # if summary.unmatched_transactions:
        #     print(f"❌ Unmatched Transactions ({len(summary.unmatched_transactions)}):")
        #     for transaction in summary.unmatched_transactions:
        #         print(f"   • {transaction.reference}: {transaction.description}")
        #     print()
        
        # Show unmatched invoices
        if summary.unmatched_invoices:
            print(f"📄 Unmatched Invoices ({len(summary.unmatched_invoices)}):")
            for invoice in summary.unmatched_invoices:
                print(f"   • {invoice.invoice_number} ({Path(invoice.file_path).name})")
            print()
        
        # Summary for next steps
        if summary.matched_pairs:
            print("🚀 Next Steps:")
            print("   - Review matched pairs above")
            print("   - The matched PDF files can be uploaded to SnelStart")
            print("   - Check unmatched items for manual processing")
        
    except Exception as e:
        print(f"❌ Error during matching: {e}")
        return
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()