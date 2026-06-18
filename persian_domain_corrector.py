# -*- coding: utf-8 -*-
"""
Domain-aware correction for the TRex / Trigger Price Action (سبک تیرکس) lessons.

Speech-to-text engines mis-spell domain jargon that is spoken with a colloquial
accent (e.g. «تیرکس» heard as «تیکس», «کندل» as «قند»). Two mechanisms fight that:

1. WHISPER_INITIAL_PROMPT — a short, natural paragraph that primes Whisper with the
   correct spellings BEFORE transcription, so most terms come out right at the source.
2. correct_text() — a *conservative* post-processing pass that only rewrites
   high-confidence, unambiguous mistakes, so it never corrupts already-good output.

Keep CORRECTIONS conservative: when in doubt, leave the text alone.
"""

import re

# ---------------------------------------------------------------------------
# Canonical domain vocabulary (correct spellings). Used to build the Whisper
# prompt and as a reference for anyone extending the corrections below.
# ---------------------------------------------------------------------------
TREX_GLOSSARY = [
    "سبک تیرکس", "تریگر پرایس اکشن", "استاد سعید خاکستر",
    "کندل", "ای تی آر", "لگ", "بیس", "رالی", "دراپ", "پولبک", "پولک",
    "رالی بیس رالی", "دراپ بیس رالی", "پیوت", "گره معاملاتی", "سی پی",
    "اف تی سی", "آر تی پی", "اف تی آر", "ای تی آر حرکتی",
    "مستر کندل", "لانگ بار", "اسپایک", "فلیپ", "هانت", "اسپایک قوی",
    "تایم فریم", "ساختار", "تریگر", "ویکلی", "دیلی", "مانتلی",
    "تایم فریم پنج دقیقه", "تایم فریم یک ساعته", "تایم فریم چهار ساعته",
    "حمایت", "مقاومت", "سطح", "روند", "کلوز", "های قیمت", "لو قیمت",
]

# A natural-sounding paragraph in the speaker's own register. Whisper uses this as
# context, biasing it toward these spellings. Keep it under ~200 tokens.
WHISPER_INITIAL_PROMPT = (
    "این جلسه از دوره‌ی سبک تیرکس و تریگر پرایس اکشن استاد سعید خاکستر است. "
    "در این سبک بازار از الگوی رالی بیس رالی و دراپ بیس رالی تشکیل شده. "
    "کوچکترین حرکت بازار را پولک می‌گوییم و سه پولبک در یک راستا یک لگ می‌سازد. "
    "لگ بر اساس ای تی آر حرکتی اندازه‌گیری می‌شود و از یک بیس یا گره معاملاتی شروع می‌شود. "
    "وقتی سه کندل در یک راستا و یک کندل برگشت داشته باشیم پیوت داریم. "
    "بعد از پیوت، اف تی سی و آر تی پی را در تایم فریم ویکلی، دیلی، چهار ساعته، یک ساعته، "
    "پنج دقیقه و یک دقیقه بررسی می‌کنیم. مفاهیم مستر کندل، لانگ بار، اسپایک، فلیپ و هانت هم مهم‌اند."
)

# Comma-separated hotwords passed to faster-whisper to bias decoding toward the
# domain vocabulary (stronger and more targeted than initial_prompt for terms).
WHISPER_HOTWORDS = "، ".join([
    "تیرکس", "تریگر پرایس اکشن", "سعید خاکستر", "کندل", "ای تی آر",
    "لگ", "بیس", "رالی", "دراپ", "پولبک", "پولک", "پیوت", "گره معاملاتی",
    "اف تی سی", "آر تی پی", "مستر کندل", "لانگ بار", "اسپایک", "تایم فریم",
])

# Persian letter range used for word-boundary lookarounds (\b is unreliable here).
_FA = r"؀-ۿ"


def _word(pattern: str) -> str:
    """Wrap a pattern so it only matches as a standalone token (not inside a word)."""
    return rf"(?<![{_FA}]){pattern}(?![{_FA}])"


# ---------------------------------------------------------------------------
# Conservative corrections. Each entry: (compiled_regex, replacement).
# Only add a rule when the wrong form is essentially never a valid Persian word
# in this context, so we can replace it safely.
# ---------------------------------------------------------------------------
_RAW_CORRECTIONS = [
    # --- "سبک تریگر پرایس اکشن" (the methodology name) ------------------------
    # Normalize the «پرایس اکشن» spelling first, however the spaces fall
    # (پرای سکشن / پرایسکشن / پرایس اکشن / پرای اسکشن ...).
    (r"پرای\s*(?:س\s*ا?کشن|ا?سکشن)", "پرایس اکشن"),
    # «تریگر» mis-heard as دیرگیر / گیرگیر / تیرگر.
    (_word(r"(?:دیرگیر|گیرگیر|تیرگر|تریگه)"), "تریگر"),
    # A wrong prefix word right before «تریگر پرایس اکشن» is really «سبک».
    (r"(?:صفحه|صحبت|صحب|سبکه?)\s+(?=تریگر\s+پرایس\s+اکشن)", "سبک "),

    # --- Style / proper names -------------------------------------------------
    # «تیرکس» mis-heard as تیکس / تی کس / تیرکست. Not a real Persian word otherwise.
    (_word(r"تی\s*کس(?:ت)?"), "تیرکس"),
    (_word(r"تیرکست"), "تیرکس"),
    # «خاکستر» (the master's surname). فاکستر is never a word; خاکستان/خاکستری
    # only get fixed right after استاد/سعید so we never touch unrelated words.
    (_word(r"فاکستر[وه]?"), "خاکستر"),
    (r"(?<=سعید )خاکست(?:ان|ری|ر[وه])", "خاکستر"),
    (r"(?<=استاد )خاکست(?:ان|ری|ر[وه])", "خاکستر"),
    (_word(r"خاکستر[وه]"), "خاکستر"),

    # --- Speaker self-intro --------------------------------------------------
    # «بنده قائدی هستم»: ونده/بنده + قایدی/قائدی.
    (_word(r"ونده(?=\s+قا)"), "بنده"),
    (_word(r"قایدی"), "قائدی"),

    # --- Acronyms written in Latin or mangled --------------------------------
    (_word(r"[fF][tT][cC]"), "اف تی سی"),
    (_word(r"[rR][tT][pP]"), "آر تی پی"),
    (_word(r"[fF][tT][rR]"), "اف تی آر"),
    (_word(r"[aA][tT][rR]"), "ای تی آر"),
    # «ام۵ / ام5 / am5» → «ام ۵» (M5 timeframe), same for m1, m15, h1, h4.
    (_word(r"[aA]?[mM]\s*5"), "ام ۵"),
    (_word(r"[aA]?[mM]\s*1\b"), "ام ۱"),
    (_word(r"[aA]?[mM]\s*15"), "ام ۱۵"),

    # --- Recurring accent mis-hearings (observed in large-v3 output) ----------
    # «افتخار می‌کنم» mis-heard as «اعتقاد می‌کنم» (اعتقاد+می‌کنم is not a real
    # collocation; one says «اعتقاد دارم», so this form is safe to rewrite).
    (r"اعتقاد(?=\s+می[‌\s]?کنم)", "افتخار"),
    (_word(r"ادغال"), "انواع"),            # «ادغال کندل» → انواع کندل
    (_word(r"حد\s+دقل"), "حداقل"),        # «حد دقل» → حداقل
    (_word(r"کچکترین"), "کوچکترین"),
    (_word(r"پولچکترین"), "کوچکترین"),
    (_word(r"فارج"), "خارج"),
    (_word(r"طوان"), "توان"),
    (r"صف(?= کندل)", "صفر"),               # «صف کندل شناسی» → صفر کندل شناسی

    # --- Broken / clipped words ----------------------------------------------
    (_word(r"نام\s*گذا"), "نام‌گذاری"),
    (_word(r"تغ\s+نمیکنه"), "تغییر نمیکنه"),
    (_word(r"متناس(?=\s)"), "متناسب"),

    # --- Spacing for ATR family ----------------------------------------------
    (_word(r"ای\s*تی\s*آر"), "ای تی آر"),
]

_CORRECTIONS = [(re.compile(p), r) for p, r in _RAW_CORRECTIONS]

# ASCII digits → Persian digits (the normalizer already handles Arabic-Indic ones).
_ASCII_TO_PERSIAN_DIGITS = {ord(str(i)): "۰۱۲۳۴۵۶۷۸۹"[i] for i in range(10)}


def to_persian_digits(text: str) -> str:
    """Convert ASCII 0-9 to Persian digits for a consistent script."""
    return text.translate(_ASCII_TO_PERSIAN_DIGITS)


def correct_text(text: str, persian_digits: bool = True) -> str:
    """Apply conservative TRex-domain corrections to transcribed text.

    Safe to run on any Persian text: rules only fire on tokens that are not
    valid words in this domain. Returns the corrected text.
    """
    if not text:
        return text

    for pattern, replacement in _CORRECTIONS:
        text = pattern.sub(replacement, text)

    if persian_digits:
        text = to_persian_digits(text)

    # Collapse any double spaces introduced by replacements.
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


if __name__ == "__main__":
    import sys
    try:  # ensure Persian prints on a Windows cp1252 console
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    samples = [
        "ما تو سبک خودمون که تیکس است کار میکنیم",
        "اینجا ftc دارم بعدش rtp میگیرم",
        "متناس با این لگ از یه بیس شروع شده",
        "تایم فریم ام5 و ام 1 رو نگاه کن",
        "نام گذا بهش میگیم اسپایک",
    ]
    for s in samples:
        print(f"- {s}\n→ {correct_text(s)}\n")
