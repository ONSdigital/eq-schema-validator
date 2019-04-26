import os
import unittest
from json import load

from structlog import configure
from structlog import getLogger
from structlog.stdlib import LoggerFactory

from app.validation.validator import Validator

logger = getLogger()

configure(logger_factory=LoggerFactory())


class TestSchemaValidation(unittest.TestCase):  # pylint: disable=too-many-public-methods

    def setUp(self):
        self.validator = Validator()

    def test_invalid_schema_block(self):
        file = 'schemas/test_invalid_routing_block.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)
        self.assertEqual(len(errors), 6)

        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. The routing rules for group or block: '
                                               'conditional-routing-block must contain a default routing rule '
                                               'without a when rule')
        self.assertEqual(errors[1]['message'], 'Schema Integrity Error. Routing rule routes to invalid block '
                                               '[invalid-location]')
        self.assertEqual(errors[2]['message'], 'Schema Integrity Error. The answer id - fake-answer in the id key of the '
                                               '"when" clause for conditional-routing-block does not exist')
        self.assertEqual(errors[3]['message'], 'Schema Integrity Error. Routing rule not defined for all answers or '
                                               'default not defined for answer [conditional-routing-answer] '
                                               "missing options [\'no\']")
        self.assertEqual(errors[4]['message'], 'Schema Integrity Error. The answer id - AnAnswerThatDoesNotExist in the id '
                                               'key of the "when" clause for response-yes does not exist')
        self.assertEqual(errors[5]['message'], 'Schema Integrity Error. The block response-yes has a repeating routing rule')

    def test_schemas(self):

        errors = []

        files = self._all_schema_files()

        for file in files:
            with open(file, encoding='utf8') as json_file:
                json_to_validate = load(json_file)

                errors.extend(self.validator.validate_schema(json_to_validate))

        if errors:
            for error in errors:
                logger.error(error)

    def test_invalid_numeric_answers(self):

        file = 'schemas/test_invalid_numeric_answers.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)
        self.assertEqual(len(errors), 9)
        self.assertEqual(
            errors[0]['message'],
            'Schema Integrity Error. Invalid range of min = 0 and max = -1.0 is possible for answer "answer-2".')
        self.assertEqual(
            errors[1]['message'],
            'Schema Integrity Error. The referenced answer "answer-1" has a greater number of decimal places than '
            'answer "answer-2"')
        self.assertEqual(
            errors[2]['message'],
            'Schema Integrity Error. The referenced answer "answer-4" can not be used to set the minimum of answer '
            '"answer-3"')
        self.assertEqual(
            errors[3]['message'],
            'Schema Integrity Error. The referenced answer "answer-5" can not be used to set the maximum of answer '
            '"answer-3"')
        self.assertEqual(
            errors[4]['message'],
            'Schema Integrity Error. Minimum value -99999999999 for answer "answer-4" is less than system limit of '
            '-999999999')
        self.assertEqual(
            errors[5]['message'],
            'Schema Integrity Error. Maximum value 99999999999 for answer "answer-4" is greater than system limit of '
            '9999999999')
        self.assertEqual(
            errors[6]['message'],
            'Schema Integrity Error. Number of decimal places 10 for answer "answer-5" is greater than system limit '
            'of 6')
        self.assertEqual(
            errors[7]['message'],
            'Schema Integrity Error. The referenced answer "answer-1" has a greater number of decimal places than '
            'answer "answer-6"')

        self.assertEqual(
            errors[8]['message'],
            'Schema Integrity Error. Default is being used with a mandatory answer: answer-7')

    def test_numeric_default_with_routing(self):

        file = 'schemas/test_numeric_default_with_routing.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(len(errors), 0)

    def test_invalid_id_in_answers_to_calculate(self):

        file = 'schemas/test_invalid_id_in_grouped_answers_to_calculate.json'
        json_to_validate = self._open_and_load_schema_file(file)

        question = json_to_validate['sections'][0]['groups'][0]['blocks'][1]['questions'][0]

        errors = self.validator.validate_calculated_ids_in_answers_to_calculate_exists(question)
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. Answer id - breakdown-3 does not exist '
                                               'within this question - breakdown-question')
        self.assertEqual(errors[1]['message'], 'Schema Integrity Error. Answer id - breakdown-4 does not exist within '
                                               'this question - breakdown-question')

    def test_invalid_date_range_period(self):

        file = 'schemas/test_invalid_date_range_period.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. The minimum period is greater than the maximum '
                                               'period for date-range-question')

    def test_invalid_mm_yyyy_date_range_period(self):

        file = 'schemas/test_invalid_mm_yyyy_date_range_period.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. Days can not be used in period_limit '
                                               'for yyyy-mm date range for date-range-question')

    def test_invalid_yyyy_date_range_period(self):

        file = 'schemas/test_invalid_yyyy_date_range_period.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. Days/Months can not be used in period_limit'
                                               ' for yyyy date range for date-range-question')

    def test_invalid_single_date_period(self):

        file = 'schemas/test_invalid_single_date_min_max_period.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. The minimum offset date is greater than the '
                                               'maximum offset date')

    def test_invalid_metadata(self):

        file = 'schemas/test_invalid_metadata.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. Metadata - ru_name not specified in metadata '
                                               'field')
        self.assertEqual(errors[1]['message'], 'Schema Integrity Error. Metadata - invalid not specified in metadata '
                                               'field')

    def test_invalid_question_titles_object(self):

        file = 'schemas/test_invalid_multiple_question_titles.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. The last value must be the default value with '
                                               'no "when" clause for single-title-question')
        self.assertEqual(errors[1]['message'], 'Schema Integrity Error. The answer id - behalf-of-answer-fake in the '
                                               'id key of the "when" clause for what-gender-question does not exist')

    def test_invalid_survey_id_whitespace(self):

        file = 'schemas/test_invalid_survey_id_whitespace.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(errors.get('message'), "'lms ' does not match '^[0-9a-z]+$'")

    def test_invalid_routing_when_answer_count(self):
        """Asserts that invalid `when` routing_rules are caught for `answer_count`"""
        file_name = 'schemas/test_invalid_routing_when_answer_count.json'
        json_to_validate = self._open_and_load_schema_file(file_name)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. The answer id - invalid-answer-id in the '
                                               'answer_ids key of the "when" clause for household-composition '
                                               'does not exist')
        self.assertEqual(errors[1]['message'], 'Schema Integrity Error. The condition "contains" is not valid '
                                               'for an answer_count based "when" clause')
        self.assertEqual(errors[2]['message'], 'Schema Integrity Error. Duplicate answer ids found within household-composition clause')
        self.assertEqual(errors[3]['message'], 'Schema Integrity Error. "answer_ids" key has to be included when type '
                                               'is "answer_count" in a "when" clause')

    def test_invalid_calculated_summary(self):
        """Asserts invalid `when` types, currencies or units are not of the same type for CalculatedSummary"""
        file_name = 'schemas/test_invalid_calculated_summary.json'
        json_to_validate = self._open_and_load_schema_file(file_name)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(len(errors), 5)
        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. '
                                               "All answers in block total-playback-type-error's answers_to_calculate "
                                               'must be of the same type')
        self.assertEqual(errors[1]['message'], 'Schema Integrity Error. '
                                               "All answers in block total-playback-currency-error's "
                                               'answers_to_calculate must be of the same currency')
        self.assertEqual(errors[2]['message'], 'Schema Integrity Error. '
                                               "All answers in block total-playback-unit-error's "
                                               'answers_to_calculate must be of the same unit')
        self.assertEqual(errors[3]['message'], 'Schema Integrity Error. '
                                               "Invalid answer id 'seventh-number-answer' in block "
                                               "total-playback-answer-error's answers_to_calculate")
        self.assertIn('Duplicate answers: ', errors[4]['message'])

    def test_answer_comparisons_different_types(self):
        """ Ensures that when answer comparison is used, the type of the variables must be the same """
        file_name = 'schemas/test_invalid_answer_comparison_types.json'
        json_to_validate = self._open_and_load_schema_file(file_name)

        errors = self.validator.validate_schema(json_to_validate)

        error_messages = [
            'Schema Integrity Error. The answers used as comparison_id "repeating-comparison-2-answer" and answer_id "repeating-comparison-1-answer" '
            'in the "when" clause for repeating-comparison have different types',
            'Schema Integrity Error. The answers used as comparison_id "route-comparison-1-answer" and answer_id "route-comparison-2-answer" '
            'in the "when" clause for route-comparison-2 have different types',
            'Schema Integrity Error. The "when" clause for comparison-3-question with conditional titles cannot contain a comparison_id',
            'Schema Integrity Error. The "when" clause for comparison-3-question with conditional titles cannot contain a comparison_id',
            'Schema Integrity Error. The answers used as comparison_id "comparison-2-answer" and answer_id "comparison-1-answer" in the "when" '
            'clause for equals-answers have different types',
            'Schema Integrity Error. The answers used as comparison_id "comparison-2-answer" and answer_id "comparison-1-answer" in the "when" '
            'clause for less-than-answers have different types',
            'Schema Integrity Error. The answers used as comparison_id "comparison-2-answer" and answer_id "comparison-1-answer" in the "when" '
            'clause for less-than-answers have different types',
            'Schema Integrity Error. The "when" clause for greater-than-answers contains a comparison_id and uses a condition of unset or set',
            'Schema Integrity Error. The "when" clause for greater-than-answers contains a comparison_id and uses a condition of unset or set',
        ]

        self.assertEqual(len(errors), len(error_messages))

        for i, error in enumerate(errors):
            self.assertEqual(error['message'], error_messages[i])

    def test_answer_comparisons_invalid_comparison_id(self):
        """ Ensures that when answer comparison is used, the comparison_id is a valid answer id"""
        file_name = 'schemas/test_invalid_answer_comparison_id.json'
        json_to_validate = self._open_and_load_schema_file(file_name)

        errors = self.validator.validate_schema(json_to_validate)

        error_messages = [
            'Schema Integrity Error. The answer id - bad-answer-id-1 in the comparison_id key of the "when" '
            'clause for repeating-comparison does not exist',
            'Schema Integrity Error. The answer id - bad-answer-id-2 in the comparison_id key of the "when" '
            'clause for route-comparison-2 does not exist',
            'Schema Integrity Error. The answer id - bad-answer-id-3 in the comparison_id key of the "when" '
            'clause for equals-answers does not exist',
            'Schema Integrity Error. The answer id - bad-answer-id-4 in the comparison_id key of the "when" '
            'clause for less-than-answers does not exist',
            'Schema Integrity Error. The answer id - bad-answer-id-5 in the comparison_id key of the "when" '
            'clause for less-than-answers does not exist',
            'Schema Integrity Error. The answer id - bad-answer-id-6 in the comparison_id key of the "when" '
            'clause for greater-than-answers does not exist',
            'Schema Integrity Error. The answer id - bad-answer-id-7 in the id key of the "when" '
            'clause for greater-than-answers does not exist',
        ]

        self.assertEqual(len(errors), len(error_messages))

        for i, error in enumerate(errors):
            self.assertEqual(error['message'], error_messages[i])

    def test_invalid_mutually_exclusive_conditions(self):

        file = 'schemas/test_invalid_mutually_exclusive_conditions.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['message'], 'Schema Integrity Error. MutuallyExclusive question type cannot contain mandatory answers.')
        self.assertEqual(errors[1]['message'], 'Schema Integrity Error. mutually-exclusive-date-answer-2 is not of type Checkbox.')

    def test_decimal_places_must_be_defined_when_using_totaliser(self):

        file = 'schemas/test_decimal_places_must_be_defined_when_using_totaliser.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['message'],
                         "Schema Integrity Error. 'decimal_places' must be defined and set to 2 for the answer_id - total-percentage")
        self.assertEqual(errors[1]['message'],
                         "Schema Integrity Error. 'decimal_places' must be defined and set to 2 for the answer_id - total-percentage-2")

    def test_metadata_defined_but_not_used_is_valid(self):
        """ Ensures that there are no errors when metadata is defined in the schema but not used """
        file_name = 'schemas/test_valid_metadata.json'
        json_to_validate = self._open_and_load_schema_file(file_name)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(0, len(errors))

    def test_invalid_piping_in_option_values(self):
        """ Ensures that there is invalid to use piping in a checkbox value """
        file = 'schemas/test_invalid_option_value.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)

        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['message'],
                         'Schema Integrity Error. Option "value" cannot contain piping. '
                         'Found in option with label - "option1" from answer_id - "checkboxanswer"')
        self.assertEqual(errors[1]['message'],
                         'Schema Integrity Error. Option "value" cannot contain piping. '
                         'Found in option with label - "option2" from answer_id - "radioanswer"')

    def test_invalid_navigation(self):
        """ Ensure that when navigation is enabled sections have title """
        file = 'schemas/test_invalid_navigation.json'
        json_to_validate = self._open_and_load_schema_file(file)

        errors = self.validator.validate_schema(json_to_validate)
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['message'],
                         'Schema Integrity Error. Section (section-1) is missing a title and navigation is enabled')
        self.assertEqual(errors[1]['message'],
                         'Schema Integrity Error. Section (section-2) is missing a title and navigation is enabled')

    def test_invalid_survey_guidance_url(self):
        """Ensure that survey with a malformed URL results in an error"""
        file = 'schemas/test_invalid_survey_guidance_url.json'
        json_to_validate = self._open_and_load_schema_file(file)

        error = self.validator.validate_schema(json_to_validate)
        self.assertRegex(error['message'], 'does not match')

    @staticmethod
    def _open_and_load_schema_file(file):
        json_file = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), file), encoding='utf8')
        json_to_validate = load(json_file)

        return json_to_validate

    @staticmethod
    def _all_schema_files():
        schema_files = []
        for folder, _, files in os.walk('schemas'):
            for filename in files:
                if filename.endswith('.json'):
                    schema_files.append(os.path.join(folder, filename))
        return schema_files


if __name__ == '__main__':
    unittest.main()
