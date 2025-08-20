#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Persian Text Normalizer with Real Texts
تست نرمال‌ساز متن فارسی با متن‌های واقعی
"""

import os
import glob
from persian_text_normalizer import PersianTextNormalizer


def test_with_real_texts():
    """Test the normalizer with real Persian texts from output directory"""
    
    print("=" * 70)
    print("تست نرمال‌ساز متن فارسی با متن‌های واقعی")
    print("Testing Persian Text Normalizer with Real Texts")
    print("=" * 70)
    
    # Initialize normalizer
    normalizer = PersianTextNormalizer()
    
    # Find all .txt files in output directory
    txt_files = glob.glob("output/*.txt")
    
    if not txt_files:
        print("❌ هیچ فایل متنی در پوشه output پیدا نشد!")
        return
    
    print(f"📁 پیدا شد {len(txt_files)} فایل متنی برای تست")
    print()
    
    total_stats = {
        'files_processed': 0,
        'total_original_chars': 0,
        'total_normalized_chars': 0,
        'total_sentences': 0,
        'total_words': 0,
        'improvements': []
    }
    
    # Process each file
    for i, txt_file in enumerate(txt_files[:5], 1):  # Test first 5 files
        filename = os.path.basename(txt_file)
        print(f"🔍 تست {i}: {filename}")
        print("-" * 50)
        
        try:
            # Read original text
            with open(txt_file, 'r', encoding='utf-8') as f:
                original_text = f.read()
            
            if not original_text.strip():
                print("⚠️  فایل خالی است")
                continue
            
            # Analyze original text
            analysis = normalizer.analyze_text(original_text)
            
            # Show statistics
            print(f"📊 آمار متن اصلی:")
            print(f"   طول متن: {analysis['original_length']:,} کاراکتر")
            print(f"   طول نرمال‌سازی شده: {analysis['normalized_length']:,} کاراکتر")
            print(f"   تعداد جملات: {analysis['sentence_count']}")
            print(f"   تعداد کلمات: {analysis['word_count']}")
            
            # Calculate improvement
            char_reduction = analysis['original_length'] - analysis['normalized_length']
            if char_reduction > 0:
                improvement = (char_reduction / analysis['original_length']) * 100
                print(f"   بهبود: {char_reduction:,} کاراکتر ({improvement:.1f}%)")
                total_stats['improvements'].append(improvement)
            
            # Show sample of normalized text
            normalized_text = analysis['normalized_text']
            sample_length = min(200, len(normalized_text))
            sample = normalized_text[:sample_length]
            
            print(f"\n📝 نمونه متن نرمال‌سازی شده:")
            print(f"   {sample}...")
            
            # Show first few sentences
            if analysis['sentences']:
                print(f"\n📝 نمونه جملات:")
                for j, sentence in enumerate(analysis['sentences'][:3], 1):
                    print(f"   {j}. {sentence}")
                if len(analysis['sentences']) > 3:
                    print(f"   ... و {len(analysis['sentences']) - 3} جمله دیگر")
            
            # Update total stats
            total_stats['files_processed'] += 1
            total_stats['total_original_chars'] += analysis['original_length']
            total_stats['total_normalized_chars'] += analysis['normalized_length']
            total_stats['total_sentences'] += analysis['sentence_count']
            total_stats['total_words'] += analysis['word_count']
            
            print()
            
        except Exception as e:
            print(f"❌ خطا در پردازش فایل {filename}: {e}")
            print()
    
    # Show overall statistics
    print("=" * 70)
    print("📊 آمار کلی")
    print("Overall Statistics")
    print("=" * 70)
    
    if total_stats['files_processed'] > 0:
        print(f"📁 فایل‌های پردازش شده: {total_stats['files_processed']}")
        print(f"📝 کل کاراکترهای اصلی: {total_stats['total_original_chars']:,}")
        print(f"📝 کل کاراکترهای نرمال‌سازی شده: {total_stats['total_normalized_chars']:,}")
        print(f"📝 کل جملات: {total_stats['total_sentences']:,}")
        print(f"📝 کل کلمات: {total_stats['total_words']:,}")
        
        # Calculate overall improvement
        total_char_reduction = total_stats['total_original_chars'] - total_stats['total_normalized_chars']
        if total_char_reduction > 0:
            overall_improvement = (total_char_reduction / total_stats['total_original_chars']) * 100
            print(f"📈 بهبود کلی: {total_char_reduction:,} کاراکتر ({overall_improvement:.1f}%)")
        
        if total_stats['improvements']:
            avg_improvement = sum(total_stats['improvements']) / len(total_stats['improvements'])
            print(f"📊 بهبود متوسط: {avg_improvement:.1f}%")
    
    print("\n✅ تست با متن‌های واقعی کامل شد!")


def test_specific_file(filename):
    """Test a specific file in detail"""
    
    print(f"🔍 تست جزئی فایل: {filename}")
    print("=" * 60)
    
    normalizer = PersianTextNormalizer()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            original_text = f.read()
        
        # Show original text sample
        print("📝 نمونه متن اصلی:")
        original_sample = original_text[:300]
        print(f"   {original_sample}...")
        print()
        
        # Normalize and analyze
        analysis = normalizer.analyze_text(original_text)
        
        # Show normalized text sample
        print("📝 نمونه متن نرمال‌سازی شده:")
        normalized_sample = analysis['normalized_text'][:300]
        print(f"   {normalized_sample}...")
        print()
        
        # Show detailed analysis
        print("📊 تحلیل جزئی:")
        print(f"   طول متن اصلی: {analysis['original_length']:,} کاراکتر")
        print(f"   طول متن نرمال‌سازی شده: {analysis['normalized_length']:,} کاراکتر")
        print(f"   تعداد جملات: {analysis['sentence_count']}")
        print(f"   تعداد کلمات: {analysis['word_count']}")
        
        if 'unique_words' in analysis:
            print(f"   کلمات منحصر به فرد: {analysis['unique_words']}")
        
        # Show all sentences
        print(f"\n📝 تمام جملات ({len(analysis['sentences'])} جمله):")
        for i, sentence in enumerate(analysis['sentences'], 1):
            print(f"   {i:2d}. {sentence}")
        
    except Exception as e:
        print(f"❌ خطا: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific file
        filename = sys.argv[1]
        if os.path.exists(filename):
            test_specific_file(filename)
        else:
            print(f"❌ فایل {filename} پیدا نشد!")
    else:
        # Test all files
        test_with_real_texts()
