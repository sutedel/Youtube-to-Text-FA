# Persian Text Normalizer with Hazm
# نرمال‌ساز متن فارسی با کتابخانه Hazm

A powerful Persian text normalization library that uses the Hazm NLP toolkit for advanced Persian text processing.

کتابخانه‌ای قدرتمند برای نرمال‌سازی متن فارسی که از ابزارهای پردازش زبان طبیعی Hazm استفاده می‌کند.

## 🎯 Features / ویژگی‌ها

### ✅ Advanced Text Normalization / نرمال‌سازی پیشرفته متن
- **Unicode Normalization**: NFC normalization for consistent character encoding
- **Arabic to Persian Conversion**: Automatic conversion of Arabic characters to Persian equivalents
- **Number Normalization**: Convert Arabic-Indic numerals to ASCII digits
- **Typography Rules**: Apply Persian typography standards (ZWNJ, punctuation, etc.)

### ✅ Sentence Segmentation / تقسیم‌بندی جملات
- **Intelligent Splitting**: Split text into meaningful sentences
- **Punctuation Handling**: Proper handling of Persian and English punctuation
- **Fallback Mechanisms**: Length-based splitting for texts without clear sentence boundaries

### ✅ Text Analysis / تحلیل متن
- **Part-of-Speech Tagging**: Identify grammatical parts of speech (when Hazm models are available)
- **Lemmatization**: Find root forms of words
- **Statistics**: Word count, sentence count, unique word analysis

### ✅ Backward Compatibility / سازگاری با نسخه‌های قبلی
- Drop-in replacement for existing `text_normalizer.py`
- Same function signatures for `normalize_text()` and `segment_sentences()`

## 🚀 Installation / نصب

### 1. Install Dependencies / نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 2. Download Hazm Models (Optional) / دانلود مدل‌های Hazm (اختیاری)
For full functionality including POS tagging and lemmatization:
```bash
# Create resources directory
mkdir -p resources

# Download models (if available)
# Note: Hazm models may need to be downloaded separately
# Check https://github.com/roshan-ai/hazm for model files
```

## 📖 Usage / استفاده

### Basic Usage / استفاده پایه
```python
from persian_text_normalizer import PersianTextNormalizer

# Initialize normalizer
normalizer = PersianTextNormalizer()

# Normalize text
text = "سلام  جهان!   من   اینجا   هستم."
normalized = normalizer.normalize_text(text)
print(normalized)
# Output: سلام جهان! من اینجا هستم.
```

### Sentence Segmentation / تقسیم‌بندی جملات
```python
long_text = """
سلام! چطور هستید؟ من خوبم. امروز هوا خیلی خوبه.
می‌خواهم برم بیرون. شما هم می‌خواهید؟
"""

sentences = normalizer.segment_sentences(long_text)
for i, sentence in enumerate(sentences, 1):
    print(f"{i}. {sentence}")
```

### Text Analysis / تحلیل متن
```python
analysis = normalizer.analyze_text(long_text)
print(f"تعداد جملات: {analysis['sentence_count']}")
print(f"تعداد کلمات: {analysis['word_count']}")
print(f"کلمات منحصر به فرد: {analysis.get('unique_words', 'N/A')}")
```

### Backward Compatibility / سازگاری با نسخه‌های قبلی
```python
from persian_text_normalizer import normalize_text, segment_sentences

# Use the same functions as before
normalized = normalize_text("سلام جهان!")
sentences = segment_sentences("سلام! چطور هستید؟")
```

## 🧪 Testing / تست

Run the test script to see the normalizer in action:
```bash
python test_persian_normalizer.py
```

This will test:
- Basic text normalization
- Arabic to Persian conversion
- Number normalization
- Persian typography rules
- Sentence segmentation
- Text analysis

## 🔧 Integration with YouTube Script / ادغام با اسکریپت YouTube

The normalizer is automatically integrated with the YouTube transcription script:

```python
# In working_youtube_to_text.py
from persian_text_normalizer import normalize_text, segment_sentences

# The script will automatically use the new normalizer
normalized_text = normalize_text(transcript_text)
sentences = segment_sentences(normalized_text)
```

## 📊 Comparison / مقایسه

### Before (Basic Normalizer) / قبل (نرمال‌ساز پایه)
```python
# Simple regex-based normalization
text = "سلام  جهان!   من   اینجا   هستم."
# Basic cleanup only
```

### After (Hazm Normalizer) / بعد (نرمال‌ساز Hazm)
```python
# Advanced NLP-based normalization
text = "سلام  جهان!   من   اینجا   هستم."
# Full Persian NLP processing including:
# - Unicode normalization
# - Arabic to Persian conversion
# - Typography rules
# - Intelligent sentence segmentation
# - Optional POS tagging and lemmatization
```

## 🎯 Benefits / مزایا

### 1. **Better Text Quality** / کیفیت بهتر متن
- More accurate Persian text normalization
- Proper handling of Arabic variants
- Consistent typography

### 2. **Advanced Analysis** / تحلیل پیشرفته
- Part-of-speech tagging
- Word lemmatization
- Detailed text statistics

### 3. **Robust Fallback** / پشتیبانی قوی
- Works even when Hazm models are not available
- Graceful degradation to basic normalization
- No breaking changes to existing code

### 4. **Academic Quality** / کیفیت دانشگاهی
- Based on established Persian NLP research
- Uses Hazm, a well-known Persian NLP toolkit
- Follows Persian language standards

## 🔍 Error Handling / مدیریت خطا

The normalizer includes comprehensive error handling:

```python
try:
    # Try to use Hazm components
    normalizer = PersianTextNormalizer()
    result = normalizer.normalize_text(text)
except Exception as e:
    # Fall back to basic normalization
    print(f"⚠️  Hazm not available: {e}")
    # Basic normalization still works
```

## 📝 Examples / مثال‌ها

### Example 1: Basic Normalization
```python
input_text = "ي ك هة إ أ آ ئ"
output = normalizer.normalize_text(input_text)
# Output: "ی ک ه ا ا آ ی"
```

### Example 2: Number Normalization
```python
input_text = "سال ٢٠٢٤ و شماره ٠١٢٣٤٥٦٧٨٩"
output = normalizer.normalize_text(input_text)
# Output: "سال 2024 و شماره 0123456789"
```

### Example 3: Typography Rules
```python
input_text = "می‌خواهم و نمی‌خواهم و بی‌خبر"
output = normalizer.normalize_text(input_text)
# Output: "می‌خواهم و نمی‌خواهم و بی‌خبر"
# (Proper ZWNJ handling)
```

## 🤝 Contributing / مشارکت

To improve the normalizer:

1. **Add Test Cases**: Add more Persian text examples to `test_persian_normalizer.py`
2. **Improve Rules**: Enhance typography rules in `_apply_persian_typography()`
3. **Add Features**: Implement additional Hazm features like dependency parsing

## 📚 References / منابع

- [Hazm Documentation](https://github.com/roshan-ai/hazm)
- [Persian NLP Best Practices](https://github.com/roshan-ai/persian-nlp-best-practices)
- [Unicode Persian](https://unicode.org/charts/PDF/U0600.pdf)

## 📄 License / مجوز

This project is open source and available under the MIT License.

---

**نکته**: این نرمال‌ساز با حفظ سازگاری با کدهای قبلی، کیفیت پردازش متن فارسی را به طور قابل توجهی بهبود می‌دهد.
