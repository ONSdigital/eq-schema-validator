import unittest

from app.validation.validator import Validator

answer = {
    "type": "Radio",
    "id": "confirm-zero-employees-answer",
    "options": [
        {"label": "Yes this is correct", "value": "Yes this is correct"},
        {"label": "No I need to change this", "value": "No I need to change this"},
    ],
    "mandatory": True,
    "q_code": "d50",
}


class TestRule(unittest.TestCase):
    @staticmethod
    def test_value_in_options():
        rule = "Yes this is correct"
        comparison = Validator.is_rule_value_valid(answer, rule)

        assert comparison is True

    @staticmethod
    def test_values_not_in_options():

        rule_list = ["Yes", "No"]
        comparison = [Validator.is_rule_value_valid(answer, rule) for rule in rule_list]
        assert all(comparison) is False

    @staticmethod
    def test_values_in_options():
        rule_list = ["Yes this is correct", "No I need to change this"]
        comparison = [Validator.is_rule_value_valid(answer, rule) for rule in rule_list]
        assert all(comparison) is True
