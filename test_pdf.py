#!/usr/bin/env python3
"""
PDF Debug Tool for German Economic Dashboard
Test PDF processing locally to debug issues
"""

import sys
import os
from pathlib import Path
from services.pdf_service import PDFService

def test_pdf_file(pdf_path: str):
    """Test a PDF file with the same service used by the dashboard."""
    
    print(f"🔍 Testing PDF: {pdf_path}")
    print("=" * 50)
    
    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return False
    
    # Get file info
    file_size = Path(pdf_path).stat().st_size
    print(f"📄 File size: {file_size / (1024*1024):.2f} MB")
    
    # Read file
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
        print(f"✅ Successfully read file")
    except Exception as e:
        print(f"❌ Could not read file: {e}")
        return False
    
    # Initialize PDF service
    pdf_service = PDFService()
    
    # Validate PDF
    print(f"\n🔍 Validating PDF format...")
    is_valid, validation_msg = pdf_service.validate_pdf(content)
    
    if is_valid:
        print(f"✅ {validation_msg}")
    else:
        print(f"❌ {validation_msg}")
        return False
    
    # Extract text
    print(f"\n📝 Extracting text...")
    try:
        text = pdf_service.extract_text_from_pdf(content)
        
        if text:
            print(f"✅ Text extraction successful!")
            print(f"   📊 Extracted {len(text)} characters")
            print(f"   📄 Word count: ~{len(text.split())} words")
            
            # Show preview
            preview = text[:500].replace('\n', ' ').strip()
            if len(preview) < len(text):
                preview += "..."
            
            print(f"\n📖 Text preview:")
            print(f"   {preview}")
            
            # Check if text is meaningful for AI processing
            if len(text.strip()) < 100:
                print(f"\n⚠️  Warning: Text is very short ({len(text)} chars)")
                print(f"   AI processing requires at least 100 characters")
                return False
            else:
                print(f"\n✅ Text length is suitable for AI processing")
                return True
                
        else:
            print(f"❌ No text extracted")
            print(f"   This could be because:")
            print(f"   • PDF contains only images/scans")
            print(f"   • PDF is password protected")  
            print(f"   • PDF uses unsupported encoding")
            print(f"   • PDF is corrupted")
            return False
            
    except Exception as e:
        print(f"❌ Text extraction failed: {e}")
        return False

def main():
    """Main function."""
    print("🏛️  PDF Debug Tool - German Economic Dashboard")
    print("=" * 55)
    
    if len(sys.argv) != 2:
        print("Usage: python test_pdf.py <path_to_pdf_file>")
        print("\nExample:")
        print("  python test_pdf.py sample_report.pdf")
        print("  python test_pdf.py /path/to/economic_report.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    success = test_pdf_file(pdf_path)
    
    print(f"\n" + "=" * 55)
    if success:
        print("🎉 PDF test PASSED - This file should work with the dashboard!")
        print("\n💡 Next steps:")
        print("   1. Upload this PDF through the dashboard interface")
        print("   2. The AI will process the text and create a report")
    else:
        print("❌ PDF test FAILED - This file won't work with the dashboard")
        print("\n💡 Suggestions:")
        print("   • Try a different PDF file")
        print("   • Use a text-based PDF (not scanned images)")
        print("   • Ensure the PDF is not password protected")
        print("   • Convert scanned PDFs using OCR software first")

if __name__ == "__main__":
    main()