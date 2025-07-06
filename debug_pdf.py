#!/usr/bin/env python3
"""
Debug script to test PDF processing and AI report generation.
This script helps identify issues with specific PDF files.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from services.pdf_service import PDFService
from services.gemini_service import GeminiService
from config import settings

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def debug_pdf_processing(pdf_path: str):
    """Debug PDF processing step by step."""
    print(f"\n{'='*60}")
    print(f"DEBUGGING PDF: {pdf_path}")
    print(f"{'='*60}")
    
    # Initialize services
    pdf_service = PDFService()
    gemini_service = GeminiService()
    
    # Check if AI service is enabled
    if not gemini_service.enabled:
        print("❌ AI service is disabled. Check your GEMINI_API_KEY configuration.")
        return
    
    try:
        # Step 1: Read the PDF file
        print("\n📖 Step 1: Reading PDF file...")
        with open(pdf_path, 'rb') as f:
            content = f.read()
        print(f"✅ File read successfully: {len(content)} bytes")
        
        # Step 2: Validate PDF
        print("\n🔍 Step 2: Validating PDF...")
        is_valid, validation_msg = pdf_service.validate_pdf(content)
        if not is_valid:
            print(f"❌ PDF validation failed: {validation_msg}")
            return
        print(f"✅ PDF validation passed: {validation_msg}")
        
        # Step 3: Extract text
        print("\n📝 Step 3: Extracting text...")
        text = pdf_service.extract_text_from_pdf(content)
        if not text or not text.strip():
            print("❌ No text could be extracted from the PDF")
            return
        
        print(f"✅ Text extraction successful: {len(text)} characters")
        print(f"📄 Text preview (first 500 chars):")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)
        
        # Step 4: Check text quality
        print(f"\n📊 Step 4: Text quality analysis...")
        print(f"   - Total characters: {len(text)}")
        print(f"   - Non-whitespace characters: {len(text.replace(' ', '').replace('\n', ''))}")
        print(f"   - Lines: {len(text.split('\n'))}")
        print(f"   - Words: {len(text.split())}")
        
        if len(text.strip()) < 100:
            print("❌ Extracted text is too short (less than 100 characters)")
            return
        
        # Step 5: Generate AI report
        print("\n🤖 Step 5: Generating AI report...")
        report_data = await gemini_service.create_report_from_text(text)
        
        if not report_data:
            print("❌ AI could not generate a structured report from the text")
            return
        
        print("✅ AI report generation successful!")
        print(f"   - Report ID: {report_data.id}")
        print(f"   - Title: {report_data.title}")
        print(f"   - Summary: {report_data.summary}")
        print(f"   - Key findings: {len(report_data.keyFindings)}")
        print(f"   - Charts: {len(report_data.charts)}")
        
        print("\n🎉 All steps completed successfully!")
        
    except FileNotFoundError:
        print(f"❌ File not found: {pdf_path}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Debug error")

def main():
    """Main function to run the debug script."""
    if len(sys.argv) != 2:
        print("Usage: python debug_pdf.py <path_to_pdf>")
        print("Example: python debug_pdf.py uploads/dwr-24-45.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ File does not exist: {pdf_path}")
        sys.exit(1)
    
    # Run the debug process
    asyncio.run(debug_pdf_processing(pdf_path))

if __name__ == "__main__":
    main() 