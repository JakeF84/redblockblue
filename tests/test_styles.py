from redblockblue.presentation.styles import CODE_STYLES, QUOTE_STYLES, CodeStyle, QuoteStyle


def test_enum_values_are_registered():
    assert CodeStyle.CLEAN.value in CODE_STYLES
    assert QuoteStyle.CINEMATIC.value in QUOTE_STYLES
