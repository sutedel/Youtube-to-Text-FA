import re
import unicodedata


def normalize_text(text: str) -> str:
	"""Normalize multilingual transcript text for readability.

	- NFC unicode normalization
	- Strip leading/trailing whitespace
	- Collapse internal whitespace
	- Normalize common Persian punctuation and numerals
	- Ensure sentences end with a single punctuation mark
	"""
	if text is None:
		return ""

	# Unicode normalize
	value = unicodedata.normalize('NFC', str(text))

	# Convert Arabic variants to Persian where common
	# Yeh: ي → ی, Kaf: ك → ک
	value = value.replace('ي', 'ی').replace('ك', 'ک')

	# Apply Persian typography rules (ZWNJ, punctuation, etc.)
	value = _apply_persian_typography(value)

	# Normalize numerals: Arabic-Indic to ASCII
	arabic_indic_digits = '٠١٢٣٤٥٦٧٨٩'
	for i, d in enumerate(arabic_indic_digits):
		value = value.replace(d, str(i))

	# Standardize punctuation spaces
	value = re.sub(r'\s*([،,:;؛.!?])\s*', r'\1 ', value)
	value = re.sub(r'\s+', ' ', value)
	value = value.strip()

	# Ensure sentence-ending punctuation
	if value and value[-1] not in '。．.؟!?！':
		value += '.'

	return value


def segment_sentences(text: str) -> list[str]:
	"""Rule-based sentence segmentation for Persian/English mixed text.

	Splits on sentence-ending punctuation while keeping punctuation attached.
	Falls back to length-based splitting if no sentence delimiters are present.
	"""
	if not text:
		return []

	value = unicodedata.normalize('NFC', str(text)).strip()
	# Normalize common sentence-ending punctuation variants
	value = value.replace('…', '...')

	# Ensure a space after sentence-ending punctuation to aid splitting
	value = re.sub(r'([.!?؟])([^\s])', r'\1 \2', value)

	# Primary split on punctuation boundaries, keep punctuation via lookbehind
	candidates = re.split(r'(?<=[.!?؟])\s+', value)

	# Cleanup: trim and drop empties
	sentences: list[str] = []
	for s in candidates:
		s = s.strip()
		if not s:
			continue
		# Merge extremely short fragments into previous sentence when possible
		if sentences and len(s.split()) <= 2:
			sentences[-1] = (sentences[-1] + ' ' + s).strip()
			continue
		sentences.append(s)

	# Fallback: if we still have a single long run without punctuation, chunk by words
	if len(sentences) <= 1:
		words = value.split()
		chunk_size = 18  # ~15-20 words per sentence
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

	# Secondary split: break overly long sentences into smaller units
	refined: list[str] = []
	for s in sentences:
		words = s.split()
		if len(words) > 40:
			# Prefer splitting by Persian/Latin commas or semicolons
			parts = re.split(r'\s*[،;,]\s+', s)
			# If comma-based split didn't help, fall back to word windows
			if len(parts) == 1:
				parts = []
				window = 22
				for i in range(0, len(words), window):
					parts.append(' '.join(words[i:i + window]))
			for idx, p in enumerate(parts):
				p = p.strip()
				if not p:
					continue
				# For comma-based sub-sentences, keep natural flow with Persian comma except the last part
				if idx < len(parts) - 1 and p[-1:] not in ['.', '!', '?', '؟', '،', ';']:
					p += '،'
				refined.append(p)
		else:
			refined.append(s)

	# Replace with refined set
	sentences = refined

	# Ensure sentences end with punctuation (respect Persian comma/semicolon)
	result: list[str] = []
	for s in sentences:
		if s and s[-1] not in '.!?؟،;':
			s = s + '.'
		result.append(s)

	return result



# --- Internal helpers ---
def _apply_persian_typography(value: str) -> str:
	"""Lightweight Persian typography normalization.

	- Remove tatweel
	- Insert ZWNJ for common prefixes/suffixes
	- Normalize ellipsis and repeated punctuation/letters
	- Standardize spacing around Persian punctuation and brackets/quotes
	"""
	if not value:
		return value

	# Remove tatweel (kashida)
	value = value.replace('ـ', '')

	# Normalize ellipsis: any 3+ dots → …
	value = re.sub(r'\.\.{2,}', '…', value)

	# Collapse repeated punctuation (!, ؟, ?, . , ،)
	value = re.sub(r'([!؟?\.،])\1{1,}', r'\1', value)

	# Reduce stretched letters (limit to 2 repeats for Persian letters)
	value = re.sub(r'([\u0600-\u06FF])\1{2,}', r'\1\1', value)

	# ZWNJ for common prefixes: می / نمی / بی
	value = re.sub(r'(?<!\S)(ن?می)[\s\u200c]+(?=[\u0600-\u06FF])', r'\1‌', value)
	value = re.sub(r'(?<!\S)(بی)[\s\u200c]+(?=[\u0600-\u06FF])', r'\1‌', value)

	# ZWNJ for common suffixes: ها / تر / ترین
	value = re.sub(r'([\u0600-\u06FF])\s+(ها|تر|ترین)\b', r'\1‌\2', value)

	# ZWNJ for Ezafe after plural: ها ی → ها‌ی
	value = re.sub(r'ها\s+ی\b', 'ها‌ی', value)

	# Convert ASCII quotes to Persian guillemets for short spans
	value = re.sub(r'"([^"\n]{1,80})"', r'«\1»', value)

	# Parentheses and guillemets spacing
	value = re.sub(r'\(\s+', '(', value)
	value = re.sub(r'\s+\)', ')', value)
	value = re.sub(r'«\s+', '«', value)
	value = re.sub(r'\s+»', '»', value)

	# Normalize comma/semicolon spacing and prefer Persian comma visually
	value = re.sub(r'\s*[،,]\s*', '، ', value)
	value = re.sub(r'\s*;\s*', '؛ ', value)

	# Prefer Persian question mark when used after Persian letters
	value = re.sub(r'([\u0600-\u06FF])\?\b', r'\1؟', value)

	# Trim spaces around punctuation produced above
	value = re.sub(r'\s+', ' ', value)
	value = value.strip()

	return value

