from app.validation.validator import Validator


def test_validate_answer_value_in_when_rule_invalid():
    when_rule = {"id": "answer-1", "condition": "equals", "value": "Yes"}
    option_value_to_answer_id_map = {
        "answer-1": {"Maybe", "No"},
        "answer-2": {"Yes", "No"},
    }

    validator = Validator()
    error_message = validator.validate_answer_value_in_when_rule(
        when_rule, option_value_to_answer_id_map
    )

    assert (
        error_message[0]["message"]
        == "Answer value in when rule with answer id `answer-1` has an invalid value of `['Yes']`"
    )


def test_validate_answer_value_in_when_rule_valid():
    when_rule = {"id": "answer-1", "condition": "equals", "value": "Yes"}
    option_value_to_answer_id_map = {
        "answer-1": {"Yes", "No"},
        "answer-2": {"Yes", "No"},
    }

    validator = Validator()
    error_message = validator.validate_answer_value_in_when_rule(
        when_rule, option_value_to_answer_id_map
    )

    assert not error_message
