from scripts.evaluate_answers import token_overlap_score


def test_token_overlap_exact_match():
    reference = "Redis is an in-memory data store."

    score = token_overlap_score(
        reference,
        reference,
    )

    assert score == 1.0


def test_token_overlap_partial_match():
    reference = "Redis is an in-memory data store."

    generated = "Redis is a data store."

    score = token_overlap_score(
        generated,
        reference,
    )

    assert 0.0 < score < 1.0


def test_token_overlap_empty_reference():
    score = token_overlap_score(
        "Redis is fast.",
        "",
    )

    assert score == 0.0