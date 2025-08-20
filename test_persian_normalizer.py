#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Persian Text Normalizer
نمونه تست برای نرمال‌ساز متن فارسی
"""

from persian_text_normalizer import PersianTextNormalizer


def test_normalizer():
    """Test the Persian text normalizer with various examples"""
    
    print("=" * 60)
    print("تست نرمال‌ساز متن فارسی با کتابخانه Hazm")
    print("Persian Text Normalizer Test with Hazm Library")
    print("=" * 60)
    
    # Initialize normalizer
    normalizer = PersianTextNormalizer()
    
    # Test cases
    test_cases = [
        # Basic normalization
        {
            "name": "نرمال‌سازی پایه",
            "input": "سلام  جهان!   من   اینجا   هستم.",
            "expected": "سلام جهان! من اینجا هستم."
        },
        
        # Arabic to Persian conversion
        {
            "name": "تبدیل حروف عربی به فارسی",
            "input": "ي ك هة إ أ آ ئ",
            "expected": "ی ک ه ا ا آ ی"
        },
        
        # Numbers normalization
        {
            "name": "نرمال‌سازی اعداد",
            "input": "سال ٢٠٢٤ و شماره ٠١٢٣٤٥٦٧٨٩",
            "expected": "سال 2024 و شماره 0123456789"
        },
        
        # Persian typography
        {
            "name": "نگارش فارسی",
            "input": "می‌خواهم و نمی‌خواهم و بی‌خبر",
            "expected": "می‌خواهم و نمی‌خواهم و بی‌خبر"
        },
        
        # Punctuation and spacing
        {
            "name": "علائم نگارشی و فاصله‌ها",
            "input": "سلام، جهان!   چطور هستید؟",
            "expected": "سلام، جهان! چطور هستید؟"
        },
        
        # Mixed content
        {
            "name": "محتوای ترکیبی",
            "input": "Hello جهان!  سلام 123 و ٤٥٦",
            "expected": "Hello جهان! سلام 123 و 456."
        }
    ]
    
    # Run tests
    passed = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🔍 تست {i}: {test['name']}")
        print(f"ورودی: {test['input']}")
        
        result = normalizer.normalize_text(test['input'])
        print(f"خروجی: {result}")
        print(f"انتظار: {test['expected']}")
        
        if result == test['expected']:
            print("✅ موفق")
            passed += 1
        else:
            print("❌ ناموفق")
        
        print("-" * 40)
    
    # Summary
    print(f"\n📊 خلاصه: {passed}/{total} تست موفق")
    
    # Test sentence segmentation
    print("\n" + "=" * 60)
    print("تست تقسیم‌بندی جملات")
    print("Sentence Segmentation Test")
    print("=" * 60)
    
    long_text = """
    سلام! چطور هستید؟ من خوبم. امروز هوا خیلی خوبه.
    می‌خواهم برم بیرون. شما هم می‌خواهید؟
    """
    
    print(f"متن اصلی:\n{long_text}")
    
    sentences = normalizer.segment_sentences(long_text)
    print(f"\nجملات تقسیم شده ({len(sentences)} جمله):")
    for i, sentence in enumerate(sentences, 1):
        print(f"{i}. {sentence}")
    
    # Test text analysis
    print("\n" + "=" * 60)
    print("تست تحلیل متن")
    print("Text Analysis Test")
    print("=" * 60)
    
    analysis = normalizer.analyze_text(long_text)
    print(f"طول متن اصلی: {analysis['original_length']}")
    print(f"طول متن نرمال‌سازی شده: {analysis['normalized_length']}")
    print(f"تعداد جملات: {analysis['sentence_count']}")
    print(f"تعداد کلمات: {analysis['word_count']}")
    
    if 'unique_words' in analysis:
        print(f"کلمات منحصر به فرد: {analysis['unique_words']}")
    
    print("\n✅ تست‌ها کامل شد!")


if __name__ == "__main__":
    test_normalizer()
