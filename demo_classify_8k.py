#!/usr/bin/env python3
"""
Demo version of the 8-K filing classification script.
This shows the pipeline working without calling the actual LLM.
"""

from src.parser.text_extractor import Filing8KTextExtractor
from src.parser.schema.event_types import ClassificationResult


def demo_classify_8k():
    """Demo the complete pipeline without LLM calls."""
    
    print("🚀 Demo: 8-K Filing Classification Pipeline")
    print("=" * 50)
    
    # Step 1: Text Extraction
    print("\n📄 Step 1: Text Extraction")
    print("-" * 30)
    
    extractor = Filing8KTextExtractor()
    
    try:
        with open('tests/fixtures/sample_8k.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        extracted_text = extractor.extract_from_html(html_content)
        
        print(f"✅ Successfully extracted {len(extracted_text)} characters")
        print(f"📝 Sample text: {extracted_text[:200]}...")
        
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        return
    
    # Step 2: Mock Classification (without LLM)
    print("\n🤖 Step 2: Event Classification")
    print("-" * 30)
    
    # Mock classification result
    mock_result = ClassificationResult(
        event_type="Financial Event",
        relevant=True,
        confidence=0.85,
        reasoning="This appears to be a quarterly earnings announcement based on the filing content and timing.",
        raw_response="Event Type: Financial Event, Relevant: true"
    )
    
    print(f"✅ Mock classification completed")
    print(f"🏷️  Event Type: {mock_result.event_type}")
    print(f"🎯 Relevant: {'Yes' if mock_result.relevant else 'No'}")
    print(f"📊 Confidence: {mock_result.confidence:.1%}")
    print(f"💭 Reasoning: {mock_result.reasoning}")
    
    # Step 3: Complete Pipeline Summary
    print("\n📋 Step 3: Pipeline Summary")
    print("-" * 30)
    
    print(f"📁 Input File: tests/fixtures/sample_8k.html")
    print(f"📄 Text Length: {len(extracted_text):,} characters")
    print(f"🏷️  Classification: {mock_result.event_type}")
    print(f"✅ Pipeline Status: Complete")
    
    print("\n🎉 Demo completed successfully!")
    print("\n💡 To run with actual LLM classification:")
    print("   # Local file:")
    print("   python classify_8k.py tests/fixtures/sample_8k.html")
    print("   # SEC URL:")
    print('   python classify_8k.py "https://www.sec.gov/Archives/edgar/data/320193/..."')


if __name__ == "__main__":
    demo_classify_8k() 