import pathlib

import os
from json import load

from jsonschema import SchemaError, RefResolver, validate, ValidationError

MAX_NUMBER = 9999999999
MIN_NUMBER = -999999999
MAX_DECIMAL_PLACES = 6


class Validator:

    def __init__(self):
        with open('schemas/questionnaire_v1.json', encoding='utf8') as schema_data:
            self.schema = load(schema_data)

    def validate_schema(self, json_to_validate):

        schema_errors = self._validate_json_against_schema(json_to_validate)

        if schema_errors:
            return schema_errors

        errors = []

        errors.extend(self.validate_schema_contains_valid_routing_rules(json_to_validate))

        errors.extend(self.validate_routing_rules_has_default_if_not_all_answers_routed(json_to_validate))

        errors.extend(self.validate_range_types_from_answers(json_to_validate))

        ignored_keys = ['routing_rules', 'skip_conditions']
        errors.extend(self.validate_duplicates(json_to_validate, ignored_keys, 'id'))
        errors.extend(self.validate_duplicates(json_to_validate, ignored_keys, 'alias'))

        errors.extend(self.validate_contains_confirmation_or_summary(json_to_validate))

        errors.extend(self.validate_child_answers_define_parent(json_to_validate))

        return errors

    def _validate_json_against_schema(self, json_to_validate):
        try:
            base_uri = pathlib.Path(os.path.abspath('schemas/questionnaire_v1.json')).as_uri()
            resolver = RefResolver(base_uri=base_uri, referrer=self.schema)
            validate(json_to_validate, self.schema, resolver=resolver)
            return []
        except ValidationError as e:
            return {
                'message': e.message,
                'path': str(e.path),
            }
        except SchemaError as e:
            return '{}'.format(e)

    def validate_schema_contains_valid_routing_rules(self, json_to_validate):

        errors = []

        blocks = self._get_blocks(json_to_validate)
        for block in blocks:
            if 'routing_rules' in block and block['routing_rules']:
                for rule in block['routing_rules']:
                    if 'goto' in rule and 'id' in rule['goto'].keys():
                        block_id = rule['goto']['id']
                        if block_id == 'summary':
                            continue

                        if not self._contains_block(json_to_validate, block_id):
                            invalid_block_error = 'Routing rule routes to invalid block [{}]'.format(block_id)
                            errors.append(self._error_message(invalid_block_error))

                    if 'goto' in rule and 'group' in rule['goto'].keys():
                        group_id = rule['goto']['group']

                        if not self._contains_group(json_to_validate, group_id):
                            invalid_group_error = 'Routing rule routes to invalid group [{}]'.format(group_id)
                            errors.append(self._error_message(invalid_group_error))

        return errors

    def validate_routing_rules_has_default_if_not_all_answers_routed(self, json_to_validate):

        errors = []

        for block in self._get_blocks(json_to_validate):
            for question in block.get('questions', []):
                for answer in question.get('answers', []):
                    errors.extend(self.validate_answer(block, answer))

        return errors

    def validate_answer(self, block, answer):
        answer_errors = []
        if 'routing_rules' in block and block['routing_rules'] and 'options' in answer:
            options = [option['value'] for option in answer['options']]
            has_default_route = False

            for rule in block['routing_rules']:
                if 'goto' in rule and 'when' in rule['goto'].keys():
                    when = rule['goto']['when']
                    if 'id' in when and when['id'] == answer['id'] and when['value'] in options:
                        options.remove(when['value'])
                else:
                    options = []
                    has_default_route = True

            has_unrouted_options = options and len(options) != len(answer['options'])

            if answer['mandatory'] is False and not has_default_route:
                default_route_not_defined = 'Default route not defined for optional question [{}]'.format(answer['id'])
                answer_errors.append(self._error_message(default_route_not_defined))

            if has_unrouted_options:
                unrouted_error_template = 'Routing rule not defined for all answers or default not defined ' \
                                          'for answer [{}] missing options {}'
                unrouted_error = unrouted_error_template.format(answer['id'], options)
                answer_errors.append(self._error_message(unrouted_error))
        return answer_errors

    def validate_range_types_from_answers(self, json_to_validate):
        errors = []

        for block in self._get_blocks(json_to_validate):
            for answer in self._get_answers_for_block(block):
                used_answers = []
                values = []
                answer_id = answer['id']
                answer_decimals = answer.get('decimal_places', 0)

                if answer.get('max_value') and 'value' in answer.get('max_value'):
                    values.append(answer['max_value']['value'])

                if answer.get('max_value') and 'answer_id' in answer.get('max_value'):
                    used_answers.append(answer['max_value']['answer_id'])

                if answer.get('min_value') and 'value' in answer.get('min_value'):
                    values.append(answer['min_value']['value'])

                if answer.get('min_value') and 'answer_id' in answer.get('min_value'):
                    used_answers.append(answer['min_value']['answer_id'])

                for value in values:
                    errors.extend(self.validate_range_value(value, answer_id, answer_decimals))

                for used_answer_id in used_answers:
                    errors.extend(self._validate_range_type(
                        json_to_validate, used_answer_id, answer_id, answer_decimals))
                    errors.extend(self._validate_min_max_ranges(
                        json_to_validate, answer_id, used_answers, used_answer_id))

        return errors

    def _get_min_max_answer_range(self, json_to_validate, used_answers):
        dict_of_answer_ranges = {}
        used_answer = {}

        for block in self._get_blocks(json_to_validate):
            for answer in self._get_answers_for_block(block):
                if answer.get('id') in used_answers:
                    used_answer[answer.get('id')] = answer

                result = self._get_range_for_answer(answer, used_answer)
                dict_of_answer_ranges[answer.get('id')] = result

        return dict_of_answer_ranges

    def _get_range_for_answer(self, answer, used_answer):
        answer_decimals = answer.get('decimal_places', 0)
        maximum = answer.get('max_value')
        minimum = answer.get('min_value')

        max_range = MAX_NUMBER
        min_range = MIN_NUMBER

        if maximum:
            return self._get_maximum_range(used_answer, answer_decimals, maximum, minimum)
        if minimum:
            return self._get_minimum_range(used_answer, answer_decimals, maximum, minimum)

        return answer, range(min_range, max_range)

    def _get_maximum_range(self, used_answer, answer_decimals, maximum, minimum):
        max_value = maximum.get('value')
        max_exclusive = maximum.get('exclusive', False)

        if max_exclusive is True:
            max_range = self._get_exclusive_range(max_value, used_answer, answer_decimals, maximum, minimum,
                                                  maximum.get('answer_id'))
        elif not max_exclusive:
            max_range = self._get_non_exclusive_range(max_value, used_answer, maximum.get('answer_id'))

        return max_range

    def _get_minimum_range(self, used_answer, answer_decimals, maximum, minimum):
        min_value = minimum.get('value')
        min_exclusive = minimum.get('exclusive', False)

        if min_exclusive is True:
            min_range = self._get_exclusive_range(min_value, used_answer, answer_decimals, maximum, minimum,
                                                  minimum.get('answer_id'))
        elif not min_exclusive:
            min_range = self._get_non_exclusive_range(min_value, used_answer, minimum.get('answer_id'))

        return min_range

    def _get_exclusive_range(self, value, used_answer, answer_decimals, maximum, minimum, answer_id):
        if value is not None:
            return self._calculate_min_max(maximum, minimum)(value, answer_decimals)
        if used_answer and maximum:
            return self._get_min_max_range_for_used_answer(used_answer, answer_id) - (1 / 10 ** answer_decimals)
        if used_answer and minimum:
            return self._get_min_max_range_for_used_answer(used_answer, answer_id) + (1 / 10 ** answer_decimals)

    def _get_non_exclusive_range(self, value, used_answer, answer_id):
        if value is not None:
            return value
        elif used_answer:
            return self._get_min_max_range_for_used_answer(used_answer, answer_id)

    def _get_min_max_range_for_used_answer(self, used_answer, answer_id):
        return self._get_range_for_answer(used_answer.get(answer_id), used_answer)

    def _validate_min_max_ranges(self, json_to_validate, answer_id, used_answers, used_answer_id):
        exclusivity_errors = []
        dict_of_answer_ranges = self._get_min_max_answer_range(json_to_validate, used_answers)

        error_message = 'The range of {} is outside the range of {}'.format(answer_id, used_answer_id)

        for block in self._get_blocks(json_to_validate):
            for answer in self._get_answers_for_block(block):

                if used_answer_id in answer:
                    answer_range = self._get_min_max_answer_range(answer)
                    used_answer_range = dict_of_answer_ranges.get(used_answer_id)

                    if answer_range < used_answer_range:
                        continue
                    else:
                        return [self._error_message(error_message)]

        exclusivity_errors.append(self._error_message(error_message))

        return exclusivity_errors

    def _validate_range_type(self, json_to_validate, used_answer_id, answer_id, answer_decimals):
        range_errors = []

        used_answer_exists = False
        for block in self._get_blocks(json_to_validate):
            for answer in self._get_answers_for_block(block):
                if answer.get('id') == used_answer_id:
                    used_answer_exists = True
                    used_answer_type = answer['type']
                    used_answer_decimals = int(answer.get('decimal_places', 0))

        if not used_answer_exists:
            error_message = '{} used for {} is not an answer id in schemas'.format(used_answer_id, answer_id)
            range_errors.append(self._error_message(error_message))
        elif used_answer_type not in ['Number', 'Currency', 'Percentage']:
            error_message = '{} is of type {} and therefore can not be passed to max/min values for {}'\
                .format(used_answer_id, used_answer_type, answer_id)
            range_errors.append(self._error_message(error_message))
        elif used_answer_decimals > answer_decimals:
            if answer_decimals == 0:
                error_message = '{} of type decimal is being passed to ' \
                                'max/min value for {} of type integer'.format(used_answer_id, answer_id)
            else:
                error_message = '{} is of type decimal with {} places is being passed to' \
                                ' max/min value for {} of {} decimal_places'\
                    .format(used_answer_id, used_answer_decimals, answer_id, answer_decimals)

            range_errors.append(self._error_message(error_message))

        return range_errors

    def validate_range_value(self, value, answer_id, answer_decimals):
        error_message = 'Decimal Places used in {} should be less than or equal to {}, currently {}' \
            .format(answer_id, MAX_DECIMAL_PLACES, answer_decimals)

        if answer_decimals > MAX_DECIMAL_PLACES:
            return [self._error_message(error_message)]

        error_message = 'Value {} used in {} should be between system limits {} to {}'\
            .format(value, answer_id, MIN_NUMBER, MAX_NUMBER)

        if MIN_NUMBER <= value <= MAX_NUMBER:
            return []

        return [self._error_message(error_message)]

    def validate_duplicates(self, json_to_validate, ignored_keys, special_key):
        unique_items = []
        duplicate_errors = []

        for value in self._parse_values(json_to_validate, ignored_keys, special_key):
            if value in unique_items:
                duplicate_errors.append(self._error_message('Duplicate {} found. value {}'.format(special_key, value)))
            else:
                unique_items.append(value)

        return duplicate_errors

    def validate_contains_confirmation_or_summary(self, json_to_validate):
        blocks = self._get_blocks(json_to_validate)
        for block in blocks:
            if block['type'] in ['Summary', 'Confirmation']:
                return []

        return [self._error_message('Schemas does not have a confirmation or summary page')]

    def validate_child_answers_define_parent(self, json_to_validate):
        errors = []

        for block in self._get_blocks(json_to_validate):
            answers_by_id = self._get_answers_by_id_for_block(block)

            for answer_id, answer in answers_by_id.items():
                if answer['type'] in ['Radio', 'Checkbox']:
                    child_answer_ids = (o['child_answer_id'] for o in answer['options'] if 'child_answer_id' in o
                                        and o['child_answer_id'])

                    for child_answer_id in child_answer_ids:
                        if child_answer_id not in answers_by_id:
                            errors.extend([self._error_message('Child answer with id %s does not exist in schemas'
                                                               % (child_answer_id))])
                            continue
                        if 'parent_answer_id' not in answers_by_id[child_answer_id]:
                            errors.extend([self._error_message('Child answer %s does not define parent_answer_id %s '
                                                               'in schemas' % (child_answer_id, answer_id))])
                            continue
                        if answers_by_id[child_answer_id]['parent_answer_id'] != answer_id:
                            errors.extend([self._error_message('Child answer %s defines incorrect parent_answer_id %s '
                                                               'in schemas: Should be %s'
                                                               % (child_answer_id, answers_by_id[child_answer_id]['parent_answer_id'],
                                                                  answer_id))])
                            continue

        return errors

    @staticmethod
    def _get_blocks(survey_json):
        for group in survey_json['groups']:
            for block in group['blocks']:
                yield block

    @staticmethod
    def _get_groups(survey_json):
        for group in survey_json['groups']:
            yield group

    @staticmethod
    def _get_answers_by_id_for_block(block_json):
        answers = {}
        for question_json in block_json.get('questions', []):
            for answer_json in question_json['answers']:
                answers[answer_json['id']] = answer_json
        return answers

    @staticmethod
    def _error_message(message):
        return {'message': 'Schema Integrity Error. {}'.format(message)}

    @staticmethod
    def _get_answers_for_block(block_json):
        answers = []
        for question_json in block_json.get('questions', []):
            for answer_json in question_json['answers']:
                answers.append(answer_json)
        return answers

    def _contains_group(self, json, group_id):
        matching_groups = [g for g in self._get_groups(json) if g['id'] == group_id]
        return len(matching_groups) == 1

    def _contains_block(self, json, block_id):
        matching_blocks = [b for b in self._get_blocks(json) if b['id'] == block_id]
        return len(matching_blocks) == 1

    def _parse_values(self, schema_json, ignored_keys, parsed_key):
        for key, value in schema_json.items():
            if key == parsed_key:
                yield value
            elif key in ignored_keys:
                continue
            elif isinstance(value, dict):
                yield from self._parse_values(value, ignored_keys, parsed_key)
            elif isinstance(value, list):
                for schema_item in value:
                    if isinstance(schema_item, dict):
                        yield from self._parse_values(schema_item, ignored_keys, parsed_key)

    @staticmethod
    def _calculate_min_max(minimum, maximum):
        if maximum:
            return lambda value, answer_decimals: value - (1 / 10 ** answer_decimals)
        elif minimum:
            return lambda value, answer_decimals: value + (1 / 10 ** answer_decimals)

