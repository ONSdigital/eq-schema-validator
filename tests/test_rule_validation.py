import unittest

import app.validation.validator as validation

single_answer_id = {
    "confirm-zero-employees-answer": {
        "answer": {
            "type": "Radio",
            "id": "confirm-zero-employees-answer",
            "options": [
                {"label": "Yes this is correct", "value": "Yes this is correct"},
                {
                    "label": "No I need to change this",
                    "value": "No I need to change this",
                },
            ],
            "mandatory": True,
            "q_code": "d50",
        },
        "block": "confirm-zero-employees-block",
        "group_id": "confirmation-block",
        "section": "default-section",
    }
}

multiple_answer_ids = {
    "accommodation-type-answer": {
        "answer": {
            "id": "accommodation-type-answer",
            "mandatory": True,
            "options": [
                {
                    "description": "For example, student hall of residence, boarding school, "
                    "armed forces base, hospital, care home, prison",
                    "label": "A communal establishment",
                    "value": "A communal establishment",
                },
                {
                    "label": "A private or family household",
                    "value": "A private or family household",
                },
            ],
            "type": "Radio",
        },
        "block": "accommodation-type",
        "group_id": "personal-details-group",
        "section": "individual-section",
    },
    "proxy-answer": {
        "answer": {
            "default": "Yes",
            "id": "proxy-answer",
            "mandatory": False,
            "options": [
                {
                    "label": "No, I’m answering for myself",
                    "value": "No, I’m answering for myself",
                },
                {"label": "Yes", "value": "Yes"},
            ],
            "type": "Radio",
        },
        "block": "proxy",
        "group_id": "personal-details-group",
        "section": "individual-section",
    },
}


class TestRule(unittest.TestCase):
    @staticmethod
    def test_search_first_value_in_options():

        comparison = validation.Validator().is_rule_value_valid(
            single_answer_id, "Yes this is correct"
        )

        assert comparison is True

    @staticmethod
    def test_search_second_value_in_options():

        comparison = validation.Validator().is_rule_value_valid(
            single_answer_id, "No I need to change this"
        )

        assert comparison is True

    @staticmethod
    def test_number_rule_ignored():

        comparison = validation.Validator().is_rule_value_valid(single_answer_id, 123)

        assert comparison is True

    @staticmethod
    def test_search_second_answer_id():

        comparison = validation.Validator().is_rule_value_valid(
            multiple_answer_ids, "No, I’m answering for myself"
        )

        assert comparison is True

    @staticmethod
    def test_missing_answer_options():

        answer_id = {
            "number-of-employees-total": {
                "answer": {
                    "id": "number-of-employees-total",
                    "q_code": "50",
                    "label": "Total number of employees",
                    "mandatory": False,
                    "type": "Number",
                    "default": 0,
                },
                "block": "number-of-employees-total-block",
                "group_id": "confirmation-block",
                "section": "default-section",
            }
        }
        comparison = validation.Validator().is_rule_value_valid(answer_id, "Ignored")

        assert comparison is False
