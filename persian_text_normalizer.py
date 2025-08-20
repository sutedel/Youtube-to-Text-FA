import re
import unicodedata
from typing import List, Optional
import hazm
from hazm import Normalizer, word_tokenize, POSTagger, Lemmatizer


class PersianTextNormalizer:
    """Advanced Persian text normalizer using Hazm library"""
    
    def __init__(self):
        """Initialize Hazm components for Persian text processing"""
        try:
            self.normalizer = Normalizer()
            self.lemmatizer = Lemmatizer()
            self.postagger = POSTagger(model='resources/postagger.model')
            print("✅ Hazm components loaded successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not load Hazm components: {e}")
            print("   Falling back to basic normalization")
            self.normalizer = None
            self.lemmatizer = None
            self.postagger = None
    
    def normalize_text(self, text: str) -> str:
        """Advanced Persian text normalization using Hazm"""
        if not text:
            return ""
        
        # Basic Unicode normalization
        text = unicodedata.normalize('NFC', str(text))
        
        # Use Hazm normalizer if available
        if self.normalizer:
            try:
                text = self.normalizer.normalize(text)
            except Exception as e:
                print(f"⚠️  Hazm normalization failed: {e}")
                text = self._basic_normalize(text)
        else:
            text = self._basic_normalize(text)
        
        # Apply Persian typography rules
        text = self._apply_persian_typography(text)
        
        # Clean up whitespace and punctuation
        text = self._cleanup_text(text)
        
        return text
    
    def _basic_normalize(self, text: str) -> str:
        """Basic normalization when Hazm is not available"""
        # Convert Arabic variants to Persian
        arabic_to_persian = {
            'ي': 'ی', 'ك': 'ک', 'ة': 'ه', 'ؤ': 'و',
            'إ': 'ا', 'أ': 'ا', 'آ': 'آ', 'ئ': 'ی'
        }
        
        for arabic, persian in arabic_to_persian.items():
            text = text.replace(arabic, persian)
        
        # Normalize numerals: Arabic-Indic to ASCII
        arabic_indic_digits = '٠١٢٣٤٥٦٧٨٩'
        for i, d in enumerate(arabic_indic_digits):
            text = text.replace(d, str(i))
        
        return text
    
    def _apply_persian_typography(self, text: str) -> str:
        """Apply Persian typography rules"""
        # Remove tatweel (kashida)
        text = text.replace('ـ', '')
        
        # Normalize ellipsis
        text = re.sub(r'\.\.{2,}', '…', text)
        
        # ZWNJ for common prefixes: می / نمی / بی
        text = re.sub(r'(?<!\S)(ن?می)[\s\u200c]+(?=[\u0600-\u06FF])', r'\1‌', text)
        text = re.sub(r'(?<!\S)(بی)[\s\u200c]+(?=[\u0600-\u06FF])', r'\1‌', text)
        
        # ZWNJ for common suffixes: ها / تر / ترین
        text = re.sub(r'([\u0600-\u06FF])\s+(ها|تر|ترین)\b', r'\1‌\2', text)
        text = re.sub(r'ها\s+ی\b', 'ها‌ی', text)
        
        # Convert ASCII quotes to Persian guillemets
        text = re.sub(r'"([^"\n]{1,80})"', r'«\1»', text)
        
        # Normalize comma/semicolon spacing
        text = re.sub(r'\s*[،,]\s*', '، ', text)
        text = re.sub(r'\s*;\s*', '؛ ', text)
        
        # Prefer Persian question mark after Persian letters
        text = re.sub(r'([\u0600-\u06FF])\?\b', r'\1؟', text)
        
        return text
    
    def _cleanup_text(self, text: str) -> str:
        """Final text cleanup"""
        # Standardize punctuation spaces
        text = re.sub(r'\s*([،,:;؛.!?؟])\s*', r'\1 ', text)
        
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Ensure sentence-ending punctuation (only if not already present)
        if text and text[-1] not in '。．.؟!?！،;':
            text += '.'
        
        return text
    
    def segment_sentences(self, text: str) -> List[str]:
        """Advanced sentence segmentation for Persian text"""
        if not text:
            return []
        
        # Normalize text first
        text = self.normalize_text(text)
        
        # Use Hazm word tokenization if available
        if self.normalizer:
            try:
                # Tokenize and then reconstruct for better sentence boundaries
                words = word_tokenize(text)
                text = ' '.join(words)
            except Exception as e:
                print(f"⚠️  Hazm tokenization failed: {e}")
        
        # Normalize sentence-ending punctuation
        text = text.replace('…', '...')
        text = re.sub(r'([.!?؟])([^\s])', r'\1 \2', text)
        
        # Split on sentence boundaries
        candidates = re.split(r'(?<=[.!?؟])\s+', text)
        
        # Clean up sentences
        sentences = []
        for s in candidates:
            s = s.strip()
            if not s:
                continue
            
            # Merge very short fragments
            if sentences and len(s.split()) <= 2:
                sentences[-1] = (sentences[-1] + ' ' + s).strip()
                continue
            
            sentences.append(s)
        
        # Fallback for long text without punctuation
        if len(sentences) <= 1:
            words = text.split()
            chunk_size = 18
            fallback = []
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size]).strip()
                if not chunk:
                    continue
                if chunk[-1] not in '.!?؟':
                    chunk += '.'
                fallback.append(chunk)
            if fallback:
                sentences = fallback
        
        # Break overly long sentences
        refined = []
        for s in sentences:
            words = s.split()
            if len(words) > 40:
                # Split by Persian/Latin commas or semicolons
                parts = re.split(r'\s*[،;,]\s+', s)
                if len(parts) == 1:
                    # Fall back to word windows
                    parts = []
                    window = 22
                    for i in range(0, len(words), window):
                        parts.append(' '.join(words[i:i + window]))
                
                for idx, p in enumerate(parts):
                    p = p.strip()
                    if not p:
                        continue
                    if idx < len(parts) - 1 and p[-1:] not in ['.', '!', '?', '؟', '،', ';']:
                        p += '،'
                    refined.append(p)
            else:
                refined.append(s)
        
        # Ensure proper punctuation
        result = []
        for s in refined:
            if s and s[-1] not in '.!?؟،;':
                s = s + '.'
            result.append(s)
        
        return result
    
    def analyze_text(self, text: str) -> dict:
        """Analyze Persian text and return detailed information"""
        if not text:
            return {}
        
        normalized = self.normalize_text(text)
        sentences = self.segment_sentences(normalized)
        
        analysis = {
            'original_length': len(text),
            'normalized_length': len(normalized),
            'sentence_count': len(sentences),
            'word_count': len(normalized.split()),
            'normalized_text': normalized,
            'sentences': sentences
        }
        
        # Add Hazm analysis if available
        if self.postagger and self.lemmatizer:
            try:
                words = word_tokenize(normalized)
                pos_tags = self.postagger.tag(words)
                lemmas = [self.lemmatizer.lemmatize(word, pos) for word, pos in pos_tags]
                
                analysis['pos_analysis'] = pos_tags
                analysis['lemmas'] = lemmas
                analysis['unique_words'] = len(set(lemmas))
            except Exception as e:
                print(f"⚠️  Hazm analysis failed: {e}")
        
        return analysis


# Backward compatibility functions
def normalize_text(text: str) -> str:
    """Backward compatibility function"""
    normalizer = PersianTextNormalizer()
    return normalizer.normalize_text(text)


def segment_sentences(text: str) -> List[str]:
    """Backward compatibility function"""
    normalizer = PersianTextNormalizer()
    return normalizer.segment_sentences(text)
