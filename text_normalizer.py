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

	# Ensure sentences end with punctuation
	result: list[str] = []
	for s in sentences:
		if s and s[-1] not in '.!?؟':
			s = s + '.'
		result.append(s)

	return result


