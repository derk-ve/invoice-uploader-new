#!/usr/bin/env python3
"""
Test script for MT940 generation functionality.
"""

import sys
import os
from decimal import Decimal
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from invoice_matching.core.models import Transaction, Invoice, MatchResult, MatchingSummary
from invoice_matching.core.upload_data_generator import UploadDataGenerator


def create_sample_data():
    """Create sample matched data for testing."""
    
    # Create sample transactions (based on real data from statements.STA)
    transactions = [
        Transaction(
            amount=Decimal('-177.29'),
            description="SEPA INCASSO BEDRIJVEN DOORLOPEND Royal Canin",
            date=datetime(2025, 4, 7),
            reference="INC25015736",
            account="438661141",
            counterparty_name="ROYAL CANIN NEDERLAND B.",
            remittance_info="SIP25024251",
            counterparty_iban="NL11RABO0154634638"
        ),
        Transaction(
            amount=Decimal('-89.36'),
            description="SEPA INCASSO BEDRIJVEN DOORLOPEND Royal Canin",
            date=datetime(2025, 4, 7),
            reference="INC25015694",
            account="438661141",
            counterparty_name="ROYAL CANIN NEDERLAND B.",
            remittance_info="SIP25023473",
            counterparty_iban="NL11RABO0154634638"
        ),
        Transaction(
            amount=Decimal('-32.32'),
            description="SEPA INCASSO BEDRIJVEN DOORLOPEND Royal Canin",
            date=datetime(2025, 4, 7),
            reference="INC25015740",
            account="438661141",
            counterparty_name="ROYAL CANIN NEDERLAND B.",
            remittance_info="SIP25024327",
            counterparty_iban="NL11RABO0154634638"
        )
    ]
    
    # Create sample invoices (based on files in data/invoices/)
    invoices = [
        Invoice(
            invoice_number="SIP25024251",
            file_path="data/invoices/Factuur SIP25024251 010425.pdf",
            amount=Decimal('177.29')
        ),
        Invoice(
            invoice_number="SIP25023473", 
            file_path="data/invoices/Factuur SIP25023473 090425.pdf",
            amount=Decimal('89.36')
        ),
        Invoice(
            invoice_number="SIP25024327",
            file_path="data/invoices/Factuur SIP25024327 150425.pdf",
            amount=Decimal('32.32')
        )
    ]
    
    # Create matched pairs
    matched_pairs = []
    for i, (transaction, invoice) in enumerate(zip(transactions, invoices)):
        match_result = MatchResult(
            transaction=transaction,
            invoice=invoice,
            confidence_score=1.0,
            amount_difference=Decimal('0.00'),
            match_reasons=[f"Invoice number found in transaction remittance info"]
        )
        matched_pairs.append(match_result)
    
    # Create matching summary
    summary = MatchingSummary(
        matched_pairs=matched_pairs,
        unmatched_transactions=[],
        unmatched_invoices=[],
        total_transactions=len(transactions),
        total_invoices=len(invoices),
        match_rate=100.0,
        total_matched_amount=sum(abs(t.amount) for t in transactions)
    )
    
    return summary


def test_mt940_generation():
    """Test the MT940 generation process."""
    print("🧪 Testing MT940 Generation")
    print("=" * 50)
    
    # Create sample data
    print("📝 Creating sample matched data...")
    summary = create_sample_data()
    print(f"   ✅ Created {len(summary.matched_pairs)} matched pairs")
    
    # Initialize upload data generator
    print("\n🔧 Initializing upload data generator...")
    generator = UploadDataGenerator()
    
    # Prepare upload data
    print("\n📦 Preparing upload package...")
    try:
        upload_package = generator.prepare_upload_data(summary, temp_base_dir="temp_test")
        print("   ✅ Upload package created successfully!")
        
        # Display package summary
        print(f"\n📋 {generator.get_package_summary(upload_package)}")
        
        # Display MT940 file content
        print(f"\n📄 Generated MT940 file content:")
        print("-" * 40)
        try:
            with open(upload_package.mt940_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
        except Exception as e:
            print(f"   ❌ Could not read MT940 file: {e}")
        
        # Display PDF files
        print(f"\n📁 PDF files in package:")
        for invoice_num, pdf_path in upload_package.pdf_files.items():
            exists = "✅" if os.path.exists(pdf_path) else "❌" 
            print(f"   {exists} {invoice_num}: {pdf_path}")
        
        # Display transaction mapping
        print(f"\n🔗 Transaction mapping:")
        for trans_ref, invoice_num in upload_package.transaction_mapping.items():
            print(f"   {trans_ref} → {invoice_num}")
        
        print(f"\n🎉 Test completed successfully!")
        print(f"📂 Package location: {upload_package.temp_directory}")
        
        # Clean up (optional - comment out to inspect files)
        cleanup_choice = input("\n🗑️  Clean up temporary files? (y/N): ").lower()
        if cleanup_choice == 'y':
            generator.cleanup_upload_package(upload_package)
            print("   ✅ Cleanup completed")
        else:
            print("   📁 Files preserved for inspection")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_mt940_generation()