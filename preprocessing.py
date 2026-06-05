import re
import string
import unicodedata
from collections import Counter


# ── Language detection ────────────────────────────────────────────────────────

def detect_language(df, text_col="text", sample_n=200):
    sample = df[text_col].dropna().sample(min(sample_n, len(df)), random_state=42)
    arabic_chars, latin_chars, total_chars = 0, 0, 0

    for text in sample:
        for ch in str(text):
            if "\u0600" <= ch <= "\u06FF":
                arabic_chars += 1
            elif ch.isalpha() and ch.isascii():
                latin_chars += 1
            total_chars += 1

    if total_chars == 0:
        print("[WARN] No characters found in sample.")
        return "unknown"

    arabic_ratio = arabic_chars / total_chars
    latin_ratio = latin_chars / total_chars
    mixed_ratio = min(arabic_ratio, latin_ratio)

    print(f"\n[Language Detection]")
    print(f"  Arabic-script chars : {arabic_ratio:.1%}")
    print(f"  Latin chars         : {latin_ratio:.1%}")

    if arabic_ratio > 0.5:
        if mixed_ratio > 0.1:
            lang = "darija"   # Arabic + Latin mix = likely Darija
        else:
            lang = "arabic"
    else:
        lang = "english"

    print(f"  Detected language   : {lang.upper()}")
    print(f"  => Use: clean_{lang}(text) or clean_text(text, lang='{lang}')\n")
    return lang


# ── Arabic preprocessing ──────────────────────────────────────────────────────

# Arabic letter normalizations
ARABIC_NORM = {
    "أ": "ا", "إ": "ا", "آ": "ا",   # Normalize alef variants
    "ة": "ه",                          # Ta marbuta → ha
    "ى": "ي",                          # Alef maqsura → ya
    "ؤ": "و",                          # Waw with hamza
    "ئ": "ي",                          # Ya with hamza
}

ARABIC_STOP_WORDS = {
    "في", "من", "إلى", "على", "عن", "مع", "هذا", "هذه", "ذلك", "التي",
    "الذي", "وقد", "كان", "كانت", "يكون", "أن", "إن", "لا", "ما", "هو",
    "هي", "هم", "نحن", "أنت", "أنا", "لقد", "قد", "كل", "بعض", "غير",
    "لم", "لن", "حتى", "لكن", "أو", "و", "ف", "ب", "ل", "ك", "بعد",
    "قبل", "خلال", "حول", "بين", "عند", "منذ", "مثل", "كما", "أيضا",
}

def remove_tashkeel(text):
    """Remove Arabic diacritics"""
    tashkeel = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]")
    return tashkeel.sub("", text)

def normalize_arabic(text):
    for orig, norm in ARABIC_NORM.items():
        text = text.replace(orig, norm)
    return text

def remove_arabic_punctuation(text):
    text = re.sub(r"[،؛؟٪٫٬«»\u0600-\u0605\u061B-\u061F]", " ", text)
    text = re.sub(r"[^\u0600-\u06FF\s]", " ", text)  # keep only Arabic + whitespace
    return text

def clean_arabic(text, remove_stopwords=True):
    """Full Arabic cleaning pipeline."""
    text = str(text)
    text = remove_tashkeel(text)
    text = normalize_arabic(text)
    text = remove_arabic_punctuation(text)
    text = re.sub(r"\s+", " ", text).strip()
    if remove_stopwords:
        tokens = text.split()
        tokens = [t for t in tokens if t not in ARABIC_STOP_WORDS and len(t) > 1]
        text = " ".join(tokens)
    return text


# ── Darija preprocessing ──────────────────────────────────────────────────────

DARIJA_STOP_WORDS = ARABIC_STOP_WORDS | {
    "wach", "wach", "machi", "bzzaf", "hada", "hadi", "dyal", "dial",
    "rah", "ana", "nta", "nti", "hna", "ntuma", "huma", "kif", "fash",
    "la", "lla", "wla", "wala", "aw", "wa", "ou",
}

def clean_darija(text):
    """
    Darija-specific cleaning: handles Arabic script + Franco-Arabic (Latin) mix.
    Strategy: clean both scripts, keep both — TF-IDF char n-grams handle the rest.
    """
    text = str(text)
    # Clean Arabic portion
    text = remove_tashkeel(text)
    text = normalize_arabic(text)
    # Remove URLs, mentions, hashtags
    text = re.sub(r"http\S+|@\w+|#\w+", " ", text)
    # Remove emojis and special chars (keep Arabic + Latin + numbers)
    text = re.sub(r"[^\u0600-\u06FF\u0020-\u007Ea-zA-Z0-9\s]", " ", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip().lower()
    # Remove short tokens (single chars, noise)
    tokens = [t for t in text.split() if len(t) > 1 and t not in DARIJA_STOP_WORDS]
    return " ".join(tokens)


# ── English preprocessing ─────────────────────────────────────────────────────

ENGLISH_STOP_WORDS = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those","am","is","are",
    "was","were","be","been","being","have","has","had","having","do","does",
    "did","doing","a","an","the","and","but","if","or","because","as","until",
    "while","of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from","up","down",
    "in","out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","both","each","few","more","most",
    "other","some","such","no","nor","not","only","own","same","so","than","too",
    "very","s","t","can","will","just","don","should","now","d","ll","m","o",
    "re","ve","y","ain","aren","couldn","didn","doesn","hadn","hasn","haven",
    "isn","ma","mightn","mustn","needn","shan","shouldn","wasn","weren","won","wouldn",
}

def clean_english(text, remove_stopwords=True):
    """Full English cleaning pipeline."""
    text = str(text).lower()
    text = re.sub(r"http\S+|@\w+|#\w+", " ", text)          # URLs, mentions
    text = re.sub(r"<[^>]+>", " ", text)                      # HTML tags
    text = re.sub(r"[^a-z0-9\s]", " ", text)                 # keep letters/digits
    text = re.sub(r"\d+", " NUM ", text)                      # normalize numbers
    text = re.sub(r"\s+", " ", text).strip()
    if remove_stopwords:
        tokens = text.split()
        tokens = [t for t in tokens if t not in ENGLISH_STOP_WORDS and len(t) > 2]
        text = " ".join(tokens)
    return text


# ── Unified interface ─────────────────────────────────────────────────────────

def clean_text(text, lang="english"):
    """Single entry point. Use after detect_language()."""
    if lang == "arabic":
        return clean_arabic(text)
    elif lang == "darija":
        return clean_darija(text)
    else:
        return clean_english(text)

def preprocess_df(df, text_col="text", lang="english", new_col="clean_text"):
    df = df.copy()
    df[new_col] = df[text_col].apply(lambda x: clean_text(x, lang=lang))
    # Quick sanity check
    empty = (df[new_col].str.strip() == "").sum()
    print(f"[Preprocessing] Done. {empty}/{len(df)} rows became empty after cleaning.")
    if empty > len(df) * 0.1:
        print(f"  [WARN] >10% empty rows — check your cleaning settings or text column name.")
    return df


# ── Quick text stats ──────────────────────────────────────────────────────────

def text_stats(df, text_col="text"):
    """Print quick stats — run this during EDA."""
    lengths = df[text_col].dropna().str.split().str.len()
    print(f"\n[Text Stats: '{text_col}']")
    print(f"  Rows        : {len(df)}")
    print(f"  Nulls       : {df[text_col].isna().sum()}")
    print(f"  Avg tokens  : {lengths.mean():.1f}")
    print(f"  Median      : {lengths.median():.0f}")
    print(f"  Min/Max     : {lengths.min()} / {lengths.max()}")
    # Top unigrams
    all_words = " ".join(df[text_col].dropna()).split()
    top = Counter(all_words).most_common(10)
    print(f"  Top 10 words: {[w for w,_ in top]}")
    print()