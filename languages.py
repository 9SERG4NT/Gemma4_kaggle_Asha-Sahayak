# Language registry for ASHA Sahayak.
# Each entry: display name → native name, Whisper STT code, region.
# Whisper code = None → auto-detection is used for voice input.
# Gemma 4 E4B handles all listed languages for text/image output.

LANGUAGES: dict[str, dict] = {

    # ── SOUTH ASIAN ────────────────────────────────────────────────────────────
    "Marathi":               {"native": "मराठी",            "whisper": "mr",  "region": "South Asian"},
    "Hindi":                 {"native": "हिन्दी",           "whisper": "hi",  "region": "South Asian"},
    "Bengali":               {"native": "বাংলা",            "whisper": "bn",  "region": "South Asian"},
    "Tamil":                 {"native": "தமிழ்",            "whisper": "ta",  "region": "South Asian"},
    "Telugu":                {"native": "తెలుగు",           "whisper": "te",  "region": "South Asian"},
    "Kannada":               {"native": "ಕನ್ನಡ",            "whisper": "kn",  "region": "South Asian"},
    "Gujarati":              {"native": "ગુજરાતી",          "whisper": "gu",  "region": "South Asian"},
    "Malayalam":             {"native": "മലയാളം",           "whisper": "ml",  "region": "South Asian"},
    "Punjabi":               {"native": "ਪੰਜਾਬੀ",           "whisper": "pa",  "region": "South Asian"},
    "Urdu":                  {"native": "اردو",             "whisper": "ur",  "region": "South Asian"},
    "Odia":                  {"native": "ଓଡ଼ିଆ",            "whisper": None,  "region": "South Asian"},
    "Assamese":              {"native": "অসমীয়া",          "whisper": "as",  "region": "South Asian"},
    "Nepali":                {"native": "नेपाली",           "whisper": "ne",  "region": "South Asian"},
    "Sinhalese":             {"native": "සිංහල",            "whisper": "si",  "region": "South Asian"},
    "Sindhi":                {"native": "سنڌي",             "whisper": "sd",  "region": "South Asian"},
    "Maithili":              {"native": "मैथिली",           "whisper": None,  "region": "South Asian"},
    "Konkani":               {"native": "कोंकणी",           "whisper": None,  "region": "South Asian"},
    "Sanskrit":              {"native": "संस्कृतम्",         "whisper": "sa",  "region": "South Asian"},
    "Santali":               {"native": "ᱥᱟᱱᱛᱟᱲᱤ",          "whisper": None,  "region": "South Asian"},

    # ── SOUTHEAST ASIAN ────────────────────────────────────────────────────────
    "Thai":                  {"native": "ภาษาไทย",          "whisper": "th",  "region": "Southeast Asian"},
    "Vietnamese":            {"native": "Tiếng Việt",       "whisper": "vi",  "region": "Southeast Asian"},
    "Burmese":               {"native": "မြန်မာဘာသာ",       "whisper": "my",  "region": "Southeast Asian"},
    "Khmer":                 {"native": "ភាសាខ្មែរ",        "whisper": "km",  "region": "Southeast Asian"},
    "Indonesian":            {"native": "Bahasa Indonesia", "whisper": "id",  "region": "Southeast Asian"},
    "Filipino":              {"native": "Filipino",         "whisper": "tl",  "region": "Southeast Asian"},
    "Malay":                 {"native": "Bahasa Melayu",    "whisper": "ms",  "region": "Southeast Asian"},
    "Lao":                   {"native": "ພາສາລາວ",          "whisper": "lo",  "region": "Southeast Asian"},
    "Javanese":              {"native": "Basa Jawa",        "whisper": "jw",  "region": "Southeast Asian"},
    "Sundanese":             {"native": "Basa Sunda",       "whisper": "su",  "region": "Southeast Asian"},
    "Cebuano":               {"native": "Sinugbuanon",      "whisper": None,  "region": "Southeast Asian"},

    # ── EAST ASIAN ─────────────────────────────────────────────────────────────
    "Chinese (Simplified)":  {"native": "普通话",            "whisper": "zh",  "region": "East Asian"},
    "Chinese (Traditional)": {"native": "繁體中文",           "whisper": "zh",  "region": "East Asian"},
    "Japanese":              {"native": "日本語",            "whisper": "ja",  "region": "East Asian"},
    "Korean":                {"native": "한국어",            "whisper": "ko",  "region": "East Asian"},
    "Mongolian":             {"native": "Монгол хэл",       "whisper": "mn",  "region": "East Asian"},
    "Tibetan":               {"native": "བོད་སྐད།",          "whisper": "bo",  "region": "East Asian"},

    # ── EUROPEAN MAJOR ─────────────────────────────────────────────────────────
    "English":               {"native": "English",          "whisper": "en",  "region": "European Major"},
    "French":                {"native": "Français",         "whisper": "fr",  "region": "European Major"},
    "Spanish":               {"native": "Español",          "whisper": "es",  "region": "European Major"},
    "Portuguese":            {"native": "Português",        "whisper": "pt",  "region": "European Major"},
    "German":                {"native": "Deutsch",          "whisper": "de",  "region": "European Major"},
    "Italian":               {"native": "Italiano",         "whisper": "it",  "region": "European Major"},
    "Russian":               {"native": "Русский",          "whisper": "ru",  "region": "European Major"},
    "Polish":                {"native": "Polski",           "whisper": "pl",  "region": "European Major"},
    "Dutch":                 {"native": "Nederlands",       "whisper": "nl",  "region": "European Major"},
    "Ukrainian":             {"native": "Українська",       "whisper": "uk",  "region": "European Major"},
    "Romanian":              {"native": "Română",           "whisper": "ro",  "region": "European Major"},
    "Czech":                 {"native": "Čeština",          "whisper": "cs",  "region": "European Major"},
    "Slovak":                {"native": "Slovenčina",       "whisper": "sk",  "region": "European Major"},
    "Hungarian":             {"native": "Magyar",           "whisper": "hu",  "region": "European Major"},
    "Swedish":               {"native": "Svenska",          "whisper": "sv",  "region": "European Major"},
    "Norwegian":             {"native": "Norsk",            "whisper": "no",  "region": "European Major"},
    "Danish":                {"native": "Dansk",            "whisper": "da",  "region": "European Major"},
    "Finnish":               {"native": "Suomi",            "whisper": "fi",  "region": "European Major"},
    "Greek":                 {"native": "Ελληνικά",         "whisper": "el",  "region": "European Major"},
    "Bulgarian":             {"native": "Български",        "whisper": "bg",  "region": "European Major"},
    "Serbian":               {"native": "Српски",           "whisper": "sr",  "region": "European Major"},
    "Croatian":              {"native": "Hrvatski",         "whisper": "hr",  "region": "European Major"},
    "Slovenian":             {"native": "Slovenščina",      "whisper": "sl",  "region": "European Major"},
    "Estonian":              {"native": "Eesti",            "whisper": "et",  "region": "European Major"},
    "Latvian":               {"native": "Latviešu",         "whisper": "lv",  "region": "European Major"},
    "Lithuanian":            {"native": "Lietuvių",         "whisper": "lt",  "region": "European Major"},
    "Albanian":              {"native": "Shqip",            "whisper": "sq",  "region": "European Major"},
    "Macedonian":            {"native": "Македонски",       "whisper": "mk",  "region": "European Major"},
    "Belarusian":            {"native": "Беларуская",       "whisper": "be",  "region": "European Major"},
    "Icelandic":             {"native": "Íslenska",         "whisper": "is",  "region": "European Major"},
    "Maltese":               {"native": "Malti",            "whisper": "mt",  "region": "European Major"},
    "Turkish":               {"native": "Türkçe",           "whisper": "tr",  "region": "European Major"},
    "Georgian":              {"native": "ქართული",          "whisper": "ka",  "region": "European Major"},
    "Armenian":              {"native": "Հայերեն",          "whisper": "hy",  "region": "European Major"},
    "Afrikaans":             {"native": "Afrikaans",        "whisper": "af",  "region": "European Major"},

    # ── MIDDLE EAST & CENTRAL ASIA ─────────────────────────────────────────────
    "Arabic":                {"native": "العربية",          "whisper": "ar",  "region": "Middle East & Central Asia"},
    "Hebrew":                {"native": "עברית",            "whisper": "he",  "region": "Middle East & Central Asia"},
    "Persian (Farsi)":       {"native": "فارسی",            "whisper": "fa",  "region": "Middle East & Central Asia"},
    "Pashto":                {"native": "پښتو",             "whisper": "ps",  "region": "Middle East & Central Asia"},
    "Kurdish":               {"native": "Kurdî",            "whisper": None,  "region": "Middle East & Central Asia"},
    "Uzbek":                 {"native": "O'zbek",           "whisper": "uz",  "region": "Middle East & Central Asia"},
    "Kazakh":                {"native": "Қазақ тілі",       "whisper": "kk",  "region": "Middle East & Central Asia"},
    "Azerbaijani":           {"native": "Azərbaycan dili",  "whisper": "az",  "region": "Middle East & Central Asia"},
    "Turkmen":               {"native": "Türkmen dili",     "whisper": "tk",  "region": "Middle East & Central Asia"},
    "Kyrgyz":                {"native": "Кыргыз тили",      "whisper": None,  "region": "Middle East & Central Asia"},
    "Tajik":                 {"native": "Тоҷикӣ",           "whisper": "tg",  "region": "Middle East & Central Asia"},
    "Uyghur":                {"native": "ئۇيغۇرچە",         "whisper": None,  "region": "Middle East & Central Asia"},

    # ── SUB-SAHARAN AFRICA ─────────────────────────────────────────────────────
    "Swahili":               {"native": "Kiswahili",        "whisper": "sw",  "region": "African"},
    "Amharic":               {"native": "አማርኛ",            "whisper": "am",  "region": "African"},
    "Hausa":                 {"native": "Hausa",            "whisper": "ha",  "region": "African"},
    "Yoruba":                {"native": "Yorùbá",           "whisper": "yo",  "region": "African"},
    "Igbo":                  {"native": "Igbo",             "whisper": None,  "region": "African"},
    "Zulu":                  {"native": "isiZulu",          "whisper": None,  "region": "African"},
    "Xhosa":                 {"native": "isiXhosa",         "whisper": None,  "region": "African"},
    "Somali":                {"native": "Soomaali",         "whisper": "so",  "region": "African"},
    "Wolof":                 {"native": "Wolof",            "whisper": "wo",  "region": "African"},
    "Shona":                 {"native": "chiShona",         "whisper": "sn",  "region": "African"},
    "Oromo":                 {"native": "Afaan Oromoo",     "whisper": None,  "region": "African"},
    "Tigrinya":              {"native": "ትግርኛ",             "whisper": None,  "region": "African"},
    "Kinyarwanda":           {"native": "Ikinyarwanda",     "whisper": None,  "region": "African"},
    "Lingala":               {"native": "Lingála",          "whisper": None,  "region": "African"},
    "Chichewa":              {"native": "Chichewa",         "whisper": None,  "region": "African"},
    "Sesotho":               {"native": "Sesotho",          "whisper": None,  "region": "African"},
    "Fula":                  {"native": "Fulfulde",         "whisper": None,  "region": "African"},

    # ── EUROPEAN REGIONAL ──────────────────────────────────────────────────────
    "Welsh":                 {"native": "Cymraeg",          "whisper": "cy",  "region": "European Regional"},
    "Catalan":               {"native": "Català",           "whisper": "ca",  "region": "European Regional"},
    "Basque":                {"native": "Euskara",          "whisper": "eu",  "region": "European Regional"},
    "Irish":                 {"native": "Gaeilge",          "whisper": "ga",  "region": "European Regional"},
    "Galician":              {"native": "Galego",           "whisper": "gl",  "region": "European Regional"},
    "Occitan":               {"native": "Occitan",          "whisper": "oc",  "region": "European Regional"},
    "Breton":                {"native": "Brezhoneg",        "whisper": "br",  "region": "European Regional"},
    "Luxembourgish":         {"native": "Lëtzebuergesch",   "whisper": "lb",  "region": "European Regional"},
    "Yiddish":               {"native": "ייִדיש",            "whisper": "yi",  "region": "European Regional"},

    # ── INDIGENOUS AMERICAS ────────────────────────────────────────────────────
    "Quechua":               {"native": "Runasimi",         "whisper": None,  "region": "Indigenous Americas"},
    "Guaraní":               {"native": "Avañe'ẽ",          "whisper": None,  "region": "Indigenous Americas"},
    "Aymara":                {"native": "Aymar aru",        "whisper": None,  "region": "Indigenous Americas"},
    "Nahuatl":               {"native": "Nāhuatl",          "whisper": None,  "region": "Indigenous Americas"},
    "Haitian Creole":        {"native": "Kreyòl ayisyen",   "whisper": "ht",  "region": "Indigenous Americas"},

    # ── PACIFIC ────────────────────────────────────────────────────────────────
    "Māori":                 {"native": "Te Reo Māori",     "whisper": "mi",  "region": "Pacific"},
    "Hawaiian":              {"native": "ʻŌlelo Hawaiʻi",   "whisper": "haw", "region": "Pacific"},
    "Malagasy":              {"native": "Malagasy",         "whisper": "mg",  "region": "Pacific"},
}


def get_dropdown_choices() -> list[str]:
    """Return display strings sorted first by region order, then alphabetically."""
    region_order = [
        "South Asian",
        "Southeast Asian",
        "East Asian",
        "European Major",
        "Middle East & Central Asia",
        "African",
        "European Regional",
        "Indigenous Americas",
        "Pacific",
    ]
    choices = []
    for region in region_order:
        for lang, info in sorted(LANGUAGES.items()):
            if info["region"] == region:
                choices.append(f"{lang} ({info['native']})")
    return choices


def parse_choice(choice: str) -> str:
    """Extract the English language name from a dropdown choice string.

    Uses rfind so 'Chinese (Simplified) (普通话)' → 'Chinese (Simplified)'
    rather than splitting on the first '(' which would give 'Chinese'.
    """
    idx = choice.rfind(" (")
    return choice[:idx].strip() if idx != -1 else choice.strip()


def get_whisper_code(lang_name: str) -> str | None:
    """Return the Whisper language code for a language, or None for auto-detect."""
    return LANGUAGES.get(lang_name, {}).get("whisper")


def get_native_name(lang_name: str) -> str:
    return LANGUAGES.get(lang_name, {}).get("native", lang_name)
