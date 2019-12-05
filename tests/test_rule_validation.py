import unittest

from app.validation.validator import Validator

answer = [
    {"label": "Yes this is correct", "value": "Yes this is correct"},
    {"label": "No I need to change this", "value": "No I need to change this"},
]


class TestRule(unittest.TestCase):
    @staticmethod
    def test_value_in_options():
        when_value = "Yes this is correct"
        comparison = Validator.is_option_value_in_answer_options(when_value, answer)

        assert comparison is True

    @staticmethod
    def test_values_not_in_options():

        when_values = ["Yes", "No"]
        comparison = [
            Validator.is_option_value_in_answer_options(when_values, answer)
            for rule in when_values
        ]
        assert all(comparison) is False

    @staticmethod
    def test_values_in_options():
        when_values = ["Yes this is correct", "No I need to change this"]
        comparison = [
            Validator.is_option_value_in_answer_options(when_value, answer)
            for when_value in when_values
        ]
        assert all(comparison) is True

    @staticmethod
    def test_are_all_values_in_answer_options():
        when_values = ["Yes this is correct"]
        comparison = Validator.are_all_values_in_answer_options(when_values, answer)

        assert comparison is True

    @staticmethod
    def test_are_all_values_not_in_answer_options():

        when_values = ["Yes this is correct", "No"]
        comparison = [Validator.are_all_values_in_answer_options(when_values, answer)]
        assert all(comparison) is False
