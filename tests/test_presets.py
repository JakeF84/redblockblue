from redblockblue.characters.presets import EXPRESSION_PRESETS, ExpressionPose


def test_expression_vocabulary_is_data_driven():
    assert len(EXPRESSION_PRESETS) >= 50
    assert isinstance(EXPRESSION_PRESETS["thinking"], ExpressionPose)
    assert isinstance(EXPRESSION_PRESETS["suspicious"], ExpressionPose)
