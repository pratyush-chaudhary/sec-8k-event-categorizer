#!/usr/bin/env python3
"""
Demo script showing 8-K filing classification pipeline.

This demonstrates the main components without requiring LLM setup.
"""

from pathlib import Path
from src.parser.text_extractor import Filing8KTextExtractor
from src.parser.schema.event_types import ClassificationResult


def main():
    print("Demo: 8-K Filing Classification Pipeline")
    print("=" * 50)
    
    # Step 1: Text Extraction Demo
    print("\nStep 1: Text Extraction")
    
    sample_file = Path("tests/fixtures/sample_8k.html")
    
    if not sample_file.exists():
        print(f"Error: Sample file not found at {sample_file}")
        return
    
    try:
        extractor = Filing8KTextExtractor()
        with open(sample_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        extracted_text = extractor.extract_from_html(html_content)
        print(f"Successfully extracted {len(extracted_text)} characters")
        print(f"Sample text preview: {extracted_text[:150]}...")
        
    except Exception as e:
        print(f"Error extracting text: {e}")
        return
    
    # Step 2: Mock Classification Demo
    print("\nStep 2: Event Classification")
    print("(Using mock result - for real classification, run classify_8k.py)")
    
    # Create a mock classification result
    mock_result = ClassificationResult(
        event_type="Financial Event",
        relevant=True,
        confidence=0.85,
        reasoning="Sample Apple earnings filing contains financial results and quarterly data",
        raw_response="Event Type: Financial Event, Relevant: true"
    )
    
    print(f"Mock classification completed")
    print(f"Event Type: {mock_result.event_type}")
    print(f"Relevant: {'Yes' if mock_result.relevant else 'No'}")
    print(f"Confidence: {mock_result.confidence:.1%}")
    print(f"Reasoning: {mock_result.reasoning}")
    
    # Step 3: Summary
    print("\nStep 3: Pipeline Summary")
    print("-" * 30)
    
    print(f"Input File: tests/fixtures/sample_8k.html")
    print(f"Text Length: {len(extracted_text):,} characters")
    print(f"Classification: {mock_result.event_type}")
    print(f"Pipeline Status: Complete")
    
    print("\nDemo completed successfully!")
    print("\nTo run with actual LLM classification:")
    print("python classify_8k.py tests/fixtures/sample_8k.html")


if __name__ == "__main__":
    main() 