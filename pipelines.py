"""
pipelines.py
CSE331 - Project 09: Document Redaction & Metadata Privacy
Shared PII detectors used by redact_real_docs.py, evaluate_real_docs.py and detection_quality.py.

Detector evolution (each stage is compared in the report):
  make_detector("v1")  Presidio defaults only (built-in recognizers).
  make_detector("v2")  Presidio + spaCy en_core_web_lg  -> stronger PERSON / LOCATION NER.
  make_detector("v3")  v2 + custom US phone & US street-address regex
                       + overlap resolution (a full address wins over PERSON/LOCATION
                         fragments tagged inside it)
                       + allow-list so the non-personal decoy (hr@company.com) survives.
  make_detector("v4")  v3 + locale-aware, BILINGUAL recognizers  <-- recommended detector:
                       + Jordanian (+962 / 07x) and generic international phone numbers,
                       + Arabic-script names / addresses that the English spaCy model misses,
                       + UK / Jordan / Spain postal-address patterns.
                       This is what makes the tool fit a Jordanian university context
                       instead of a US-only pipeline.

Each detector is a function:  text -> list[RecognizerResult]
"""

# Entity types we ask Presidio to return. The custom recognizers below reuse these same
# built-in types (PHONE_NUMBER / LOCATION / PERSON) so results fold into one set.
ENTITIES = ["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "LOCATION", "US_SSN"]

# Non-personal strings that must NOT be redacted (used to measure false redactions).
ALLOW_LIST = ["hr@company.com"]

# --------------------------------------------------------------------------- phones
# US / North-American: +1-221-608-7489, 001-..., (233)916-5122, 233.916.5122x154, 555 867 5309
US_PHONE_REGEX = (
    r"(?<![\w.\-])"
    r"(?:(?:\+?1|001)[-.\s]?)?"
    r"(?:\(\d{3}\)\s?|\d{3}[-.\s]?)\d{3}[-.\s]?\d{4}"
    r"(?:\s?x\d{2,5})?"
    r"(?!\d)"
)
# Generic international, country code first: +962 79 555 1234, +44 20 7946 0958, +34 ...
INTL_PHONE_REGEX = r"(?<![\w.\-])\+\d{1,3}(?:[\s.\-]?\d){6,13}(?!\d)"
# Jordanian local mobile: 0795551234, 079 555 1234, 077-..., 078...
JO_PHONE_REGEX = r"(?<![\w.\-])07[789](?:[\s.\-]?\d){7}(?!\d)"

# --------------------------------------------------------------------------- addresses
US_ADDRESS_REGEXES = [
    # "1696 Boyd Ranch Suite 423, South Samantha, FM 46552"
    r"\b\d{1,6}\s[^,\n]{3,60},\s*[^,\n]{2,40},\s*[A-Z]{2}\s\d{5}(?:-\d{4})?",
    # military: "USS Smith, FPO AP 12345"
    r"\b(?:USNS|USS|USCGC|USNV)\s[^,\n]{2,40},\s*(?:FPO|APO|DPO)\s[A-Z]{2}\s\d{5}",
    # military: "PSC 1234, Box 5678, APO AA 12345" / "Unit 1234 Box 5678, DPO AE 12345"
    r"\b(?:PSC|Unit|CMR)\s\d+,?\s*Box\s\d+,?\s*(?:FPO|APO|DPO)\s[A-Z]{2}\s\d{5}",
]
# Locale-aware addresses added in v4
INTL_ADDRESS_REGEXES = [
    # Jordan: "Building 15, Wasfi Al-Tal Street, Amman 11181, Jordan"
    r"\bBuilding\s\d+[^,\n]{0,60},\s*[^,\n]{2,40},\s*[A-Za-z؀-ۿ]+\s\d{4,5},?\s*Jordan",
    # UK: "14 Mill Lane, Cardiff CF10 3AT, UK"
    r"\b\d{1,6}\s[^,\n]{3,40},\s*[^,\n]{2,30}\s[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2},?\s*UK",
    # Spain: "Calle Mayor 7, Madrid 28013, Spain"
    r"\bCalle\s[^,\n]{2,40},\s*[^,\n]{2,30}\s\d{5},?\s*Spain",
]

# Arabic-script personal text (names and short address phrases). The English spaCy model
# cannot see these, so without this recognizer every Arabic identifier leaks.
ARABIC_PII_REGEX = r"[؀-ۿ]+(?:\s+[؀-ۿ]+)*"

# Recognizer names, so detect() can tell custom matches from Presidio's built-ins.
US_PHONE_NAME = "UsPhoneRecognizer"
INTL_PHONE_NAME = "IntlPhoneRecognizer"
JO_PHONE_NAME = "JoPhoneRecognizer"
ADDRESS_NAME = "AddressRecognizer"
ARABIC_NAME = "ArabicPiiRecognizer"
PHONE_KEEP = {US_PHONE_NAME, INTL_PHONE_NAME, JO_PHONE_NAME}
_NAME_KEY = "recognizer_name"


def _spacy_analyzer():
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    cfg = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
    }
    nlp = NlpEngineProvider(nlp_configuration=cfg).create_engine()
    return AnalyzerEngine(nlp_engine=nlp)


def _recognizer_name(result):
    meta = getattr(result, "recognition_metadata", None) or {}
    return meta.get(_NAME_KEY)


def _overlaps(a, b):
    return a.start < b.end and b.start < a.end


def _add_custom_recognizers(analyzer, locale_aware):
    """Registers the regex recognizers shared by v3 (locale_aware=False) and v4 (True)."""
    from presidio_analyzer import Pattern, PatternRecognizer

    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="PHONE_NUMBER", name=US_PHONE_NAME,
        patterns=[Pattern("us_phone", US_PHONE_REGEX, 0.85)], supported_language="en"))

    address_regexes = list(US_ADDRESS_REGEXES)

    if locale_aware:
        analyzer.registry.add_recognizer(PatternRecognizer(
            supported_entity="PHONE_NUMBER", name=INTL_PHONE_NAME,
            patterns=[Pattern("intl_phone", INTL_PHONE_REGEX, 0.80)], supported_language="en"))
        analyzer.registry.add_recognizer(PatternRecognizer(
            supported_entity="PHONE_NUMBER", name=JO_PHONE_NAME,
            patterns=[Pattern("jo_phone", JO_PHONE_REGEX, 0.85)], supported_language="en"))
        analyzer.registry.add_recognizer(PatternRecognizer(
            supported_entity="PERSON", name=ARABIC_NAME,
            patterns=[Pattern("arabic_pii", ARABIC_PII_REGEX, 0.60)], supported_language="en"))
        address_regexes += INTL_ADDRESS_REGEXES

    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="LOCATION", name=ADDRESS_NAME,
        patterns=[Pattern(f"address_{i}", rx, 0.90) for i, rx in enumerate(address_regexes)],
        supported_language="en"))


def _make_custom_detector(locale_aware):
    analyzer = _spacy_analyzer()
    _add_custom_recognizers(analyzer, locale_aware)

    def detect(text):
        results = analyzer.analyze(text=text, language="en", entities=ENTITIES)
        # 1) trust only our phone recognizers (the built-in one flags street numbers like "1696")
        results = [
            r for r in results
            if r.entity_type != "PHONE_NUMBER" or _recognizer_name(r) in PHONE_KEEP
        ]
        # 2) allow-list: keep the non-personal decoy in the document
        results = [r for r in results if text[r.start:r.end] not in ALLOW_LIST]
        # 3) a full address wins over fragments inside it (city/street words tagged PERSON/LOCATION)
        addresses = [r for r in results if _recognizer_name(r) == ADDRESS_NAME]
        results = [
            r for r in results
            if r in addresses or not any(_overlaps(r, a) for a in addresses)
        ]
        return results

    return detect


def make_detector(version):
    from presidio_analyzer import AnalyzerEngine

    if version == "v1":
        analyzer = AnalyzerEngine()
        return lambda text: analyzer.analyze(text=text, language="en", entities=ENTITIES)

    if version == "v2":
        analyzer = _spacy_analyzer()
        return lambda text: analyzer.analyze(text=text, language="en", entities=ENTITIES)

    if version == "v3":
        return _make_custom_detector(locale_aware=False)

    if version == "v4":
        return _make_custom_detector(locale_aware=True)

    raise ValueError(f"unknown version: {version!r} (use v1, v2, v3 or v4)")
