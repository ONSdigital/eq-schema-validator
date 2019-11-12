import json

from app.validation.validator import Validator

validator = Validator()


def create_schema_with_id(schema_id):
    """
    Utility method that loads a JSON schema file and swaps out an answer Id.
    :param schema_id: The Id to use for the answer.
    :return: The JSON file with the Id swapped for schema_id
    """
    schema_path = 'tests/schemas/valid/test_schema_id_regex.json'

    with open(schema_path, encoding='utf8') as json_data:
        json_content = json.load(json_data)

        json_content['sections'][0]['groups'][0]['blocks'][0]['question']['answers'][0]['id'] = schema_id
        return json_content


def test_valid_schema_names():
    schema_names = [
        'star-wars', 'name-with-hyphens', 'this-is-a-valid-id-0', 'answer'
    ]

    for schema_name in schema_names:
        json_to_validate = create_schema_with_id(schema_name)
        schema_errors = validator.validate_json_schema(json_to_validate)

        assert schema_errors == {}


def test_invalid_schema_names():
    schema_names = [
        '!n0t-@-valid-id', 'NOT-A-VALID-ID', 'not_a_valid_id', 'not a valid id'
    ]

    for schema_name in schema_names:
        json_to_validate = create_schema_with_id(schema_name)
        schema_errors = validator.validate_json_schema(json_to_validate)

        message = schema_errors.get('message')

        assert f"'{schema_name}' does not match '^[a-z0-9][a-z0-9\\\\-]*[a-z0-9]$'" == message
