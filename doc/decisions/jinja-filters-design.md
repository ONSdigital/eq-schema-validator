# Jinja Filters Design

The current way we define piping (string interpolation) in a schema is to include jinja filters directly in the source strings. This has a number of issues:

- It's hard to read for translators.
- It's possible that the jinja filters could become corrupted during translation.
- If the way that we resolve the piped information changes, then the translations would all need to be updated.
- We can't easily parse the schema to understand what is being piped, for example to find all places where a specific answer is piped.

To resolve this we need to define an appropriate schema to resolve placeholders in a source string. When resolving placeholder values we need to cater for:

- Previous answer or metadata
- Previous answer or metadata transformed in some way e.g. formatting a number with a currency symbol
- Using multiple answers, metadata or fixed values in a transform e.g. formatting a date answer with a specific format
- Chaining transforms e.g. concatenate a name and then add a 's

## Questions not being addressed

- What will we do with filters used in variables block e.g. `period` in 1_0005?

## Group instances

No provision has been made in the schema design for group instances. It is assumed that:

- When a placeholder is used in a non-repeating group that any reference to answers resolves to all answers that match the answer id.
- When a placeholder is used in a repeating group that any reference to answers resolves to the answer that matches within the current repeat.

## Translations done in code

- Date ranges - `"{from_date} to {to_date}"`
- Duration (including pluralisation) - `"{num} years {num} months"`
- Calculate years difference - (including pluralisation) - `"{num} years"`
- Datetime - `"{date} at {time}"`

Actions:

- Date ranges and datetime should not be done the way they are as it will not allow for effective translation. Potential issue will be in the `format_date_range_no_repeated_month_year` filter.
- Calculate years difference to use `format_duration` filter rather than doing it in the same filter.

## Current filters to proposed transforms

### format_number

#### Current
```json
{
    "description": "Of the <em>{{answers['total-number-employees']|format_number}}</em> total employees employed on 14 December 2018, how many male and female employees worked the following hours?"
}
```

#### Proposed
```json
{

    "description": "Of the <em>{number_of_employees}</em> total employees employed on 14 December 2018, how many male and female employees worked the following hours?",
    "description_values": {
        "number_of_employees": [
            {
                "filter": "format_number",
                "filter_args": [
                    {
                        "source": "answers",
                        "value": "total-number-employees"
                    }
                ]
            }
        ]
    }
}
```

## format_currency

#### Current
```json
{
    "description": "Of the <em>{{format_currency(answers['total-retail-turnover-answer'])}}</em> total retail turnover, what was the value of internet sales?"
}
```

#### Proposed
```json
{

    "description": "Of the <em>{total_turnover}</em> total retail turnover, what was the value of internet sales?",
    "description_values": {
        "number_of_employees": [
            {
                 "filter": "format_currency",
                 "filter_args": [
                     {
                         "source": "answers",
                         "value": "total-retail-turnover-answer"
                     }
                 ]
            }
        ]
    }
}
```

## format_address_list

Only used in LMS, and that uses just the metadata address i.e. it doesn't use two addresses.

**Question:** Should we use the filter to determine which address to use?

#### Current
```json
{
    "description": "{{ format_address_list ([answers['address-line1'], answers['address-line2'], answers['locality'], answers['town-name'], answers['postcode']], [metadata['address_line1'], metadata['address_line2'], metadata['locality'], metadata['town_name'], metadata['postcode']]) }}"
}
```

#### Proposed
```json
{
    "description": "{address}",
    "description_values": {
        "address": [
            {
                 "filter": "format_address_list",
                 "filter_args": [
                     {
                         "source": "answers",
                         "value": [
                             "address-line1",
                             "address-line2",
                             "locality",
                             "town-name",
                             "postcode"
                         ]
                     },
                     {
                         "source": "metadata",
                         "value": [
                             "address_line1",
                             "address_line2",
                             "locality",
                             "town_name",
                             "postcode"
                         ]
                     }
                 ]
            }
        ]
    }
}
```

## get_current_date

#### Current
```json
{
    "description": "The number of visitors staying in the household on {{ get_current_date() }}"
}
```

#### Proposed
```json
{

    "description": "The number of visitors staying in the household on {current_date}",
    "description_values": {
        "current_date": [
            {
                 "filter": "get_current_date",
            }
        ]
    }
}
```

## format_date

#### Current
```json
{
    "description": "Are you able to report for the period from {{metadata['ref_p_start_date']|format_date}} to {{metadata['ref_p_end_date']|format_date}}?"
}
```

#### Proposed
```json
{

    "description": "Are you able to report for the period from {start_date} to {end_date}?",
    "description_values": {
        "start_date": [
            {
                "filter": "format_date",
            }
        ],
        "end_date": [
            {
                "filter": "format_date",
            }
        ],
    }
}
```

## format_date_custom

This example also demonstrates chaining filters - the output from `calculate_offset_from_weekday_in_last_whole_week` would be the first argument passed to the `format_date_custom` filter.

#### Current
```json
{
    "description": "Did you have a paid job, either as an employee or self-employed, in the week {{ calculate_offset_from_weekday_in_last_whole_week(collection_metadata['started_at'], {}) | format_date_custom( 'EEEE d MMMM YYYY' ) }} to {{ calculate_offset_from_weekday_in_last_whole_week(collection_metadata['started_at'], {}, 'SU') | format_date_custom( 'EEEE d MMMM YYYY' ) }}"
}
```

#### Proposed
```json
{

    "description": "Did you have a paid job, either as an employee or self-employed, in the week {from_date} to {to_date}",
    "description_values": {
        "from_date": [
            {
                "filter": "calculate_offset_from_weekday_in_last_whole_week",
                "filter_args": [
                    {
                        "source": "collection_metadata",
                        "value": "started_at"
                    },
                    {
                        "value": {}
                    }
                ]
            },
            {
                "filter": "format_date_custom",
                "filter_args": [
                    {
                        "value": "EEEE d MMMM YYYY"
                    }
                ]
            }
        ],
        "to_date": [
            {
                "filter": "calculate_offset_from_weekday_in_last_whole_week",
                "filter_args": [
                    {
                        "source": "collection_metadata",
                        "value": "started_at"
                    },
                    {
                        "value": {}
                    },
                    {
                        "value": "SU"
                    }
                ]
            },
            {
                "filter": "format_date_custom",
                "filter_args": [
                    {
                        "value": "EEEE d MMMM YYYY"
                    }
                ]
            }
        ],
    }
}
```

## format_conditional_date

#### Current
```json
{
    "description": "For the period {{ format_conditional_date (answers['period-from'], metadata['ref_p_start_date'])}} to {{ format_conditional_date (answers['period-to'], metadata['ref_p_end_date'])}}, what was the value of x's <em>total retail turnover</em>?"
}
```

#### Proposed
```json
{

    "description": "For the period {start_date} to {end_date}, what was the value of x's <em>total retail turnover</em>?",
    "description_values": {
        "start_date": [
            {
                 "filter": "format_conditional_date",
                 "filter_args": [
                     {
                         "source": "answers",
                         "value": "period-from"
                     },
                     {
                         "source": "metadata",
                         "value": "ref_p_start_date"
                     }
                 ]
            }
        ],
        "end_date": [
            {
                 "filter": "format_conditional_date",
                 "filter_args": [
                     {
                         "source": "answers",
                         "value": "period-to"
                     },
                     {
                         "source": "metadata",
                         "value": "ref_p_end_date"
                     }
                 ]
            }
        ]
    }
}
```

## calculate_offset_from_weekday_in_last_whole_week

**Needs as an option example as well**

#### Current
```json
{
    "description": "If you had been offered a job in the week starting {{ calculate_offset_from_weekday_in_last_whole_week(collection_metadata['started_at'], {}) | format_date_custom( 'EEEE d MMMM' ) }} would you be able to start before {{ calculate_offset_from_weekday_in_last_whole_week(collection_metadata['started_at'], {'weeks':2}) | format_date_custom( 'EEEE d MMMM' ) }}?"
}
```

#### Proposed
```json
{

    "description": "If you had been offered a job in the week starting {start_date} would you be able to start before {before_date}?",
    "description_values": {
        "start_date": [
            {
                "filter": "calculate_offset_from_weekday_in_last_whole_week",
                "filter_args": [
                    {
                        "source": "collection_metadata",
                        "value": "started_at"
                    },
                    {
                        "value": {}
                    }
                ]
            },
            {
                "filter": "format_date_custom",
                "filter_args": [
                    {
                        "value": "EEEE d MMMM"
                    }
                ]
            }
        ],
        "to_date": [
            {
                "filter": "calculate_offset_from_weekday_in_last_whole_week",
                "filter_args": [
                    {
                        "source": "collection_metadata",
                        "value": "started_at"
                    },
                    {
                        "value": { "weeks": 2 }
                    }
                ]
            },
            {
                "filter": "format_date_custom",
                "filter_args": [
                    {
                        "value": "EEEE d MMMM"
                    }
                ]
            }
        ],
    }
}
```

## calculate_years_difference

The `group_instance` in this example would be worked out automatically - if the answer id is one that repeats, the one relevant to the current repeat would be used.

#### Current
```json
{
    "description": "You are {{ calculate_years_difference (answers['date-of-birth-answer'][group_instance], 'now') }} old. Is this correct?"
}
```

#### Proposed
```json
{

    "description": "You are {number_of_years} old. Is this correct?",
    "description_values": {
        "number_of_years": [
            {
                 "filter": "calculate_years_difference",
                 "filter_args": [
                     {
                         "source": "answers",
                         "value": "date-of-birth-answer"
                     },
                     {
                         "value": "now"
                     }
                 ]
            }
        ]
    }
}

{
    "description": "You are {number_of_years} old. Is this correct?",
    "description_values": {
        "number_of_years": [
            {
                 "filter": "calculate_years_difference",
                 "filter_args": {
                     "start_date": {
                         "source": "answers",
                         "value": "date-of-birth-answer"
                     },
                     "end_date": {
                         "value": "now"
                     }
                 }
            }
        ]
    }
}

{
    "description": "You are {number_of_years} old. Is this correct?",
    "description_values": [
        {
            "placeholder": "number_of_years",
            "filters": [
                {
                    "filter": "calculate_years_difference",
                    "filter_args": {
                        "start_date": {
                            "source": "answers",
                            "value": "date-of-birth-answer"
                        },
                        "end_date": {
                            "value": "now"
                        }
                    }
                }
            ]
        }
    ]
}
```

## format_date_range_no_repeated_month_year (!)

**Important:** The current filter would not be possible in the new format as we can't pass the results of two distinct filters to another filter (we will only support chaining the result of one filter into another). This also addresses another issue of formatting date ranges in code.

**Needs as an option example as well**

#### Current
```json
{
    "description": "Did you have a paid job, either as an employee or self-employed, in the week {{ format_date_range_no_repeated_month_year(calculate_offset_from_weekday_in_last_whole_week(collection_metadata['started_at'], {}), calculate_offset_from_weekday_in_last_whole_week(collection_metadata['started_at'], {}, 'SU'), 'EEEE d MMMM YYYY') }}?"
}
```

#### Proposed
```json
{

    "description": "Did you have a paid job, either as an employee or self-employed, in the week {from_date} to {to_date}?",
    "description_values": {
        "from_date": [
            {
                "filter": "calculate_offset_from_weekday_in_last_whole_week",
                "filter_args": [
                    {
                        "source": "collection_metadata",
                        "value": "started_at",
                    },
                    {
                        "value": {}
                    }
                ]
            },
            {
                "filter": "format_date_custom",
                "filter_args": [
                    {
                        "value": "EEEE d MMMM YYYY"
                    }
                ]
            },
            {
                "filter": "remove_duplicate_month_year",
                "filter_args": [
                    {
                        "source": "collection_metadata",
                        "value": "started_at",
                    }
                ]
            }
        ],
        "to_date": [
            {
                "filter": "calculate_offset_from_weekday_in_last_whole_week",
                "filter_args": [
                    {
                        "source": "collection_metadata",
                        "value": "started_at"
                    },
                    {
                        "value": { "weeks": 2 }
                    }
                ]
            },
            {
                "filter": "format_date_custom",
                "filter_args": [
                    {
                        "value": "EEEE d MMMM"
                    }
                ]
            }
        ],
    }
}
```

## first_non_empty_item

#### Current
```json
{
    "description": "Did any significant changes occur to the total retail turnover for {{ first_non_empty_item(metadata['trad_as'], metadata['ru_name']) }}?"
}
```

#### Proposed
```json
{

    "description": "Did any significant changes occur to the total retail turnover for {business_name}?",
    "description_values": {
        "business_name": [
            {
                 "filter": "first_non_empty_item",
                 "filter_args": [
                     {
                         "source": "metadata",
                         "value": "trad_as"
                     },
                     {
                         "source": "metadata",
                         "value": "ru_name"
                     }
                 ]
            }
        ]
    }
}
```

## format_household_name

#### Current
```json
{
    "description": "Are you <em>{{ [answers['first-name'][group_instance], answers['middle-names'][group_instance], answers['last-name'][group_instance]] | format_household_name }}<em>?"
}
```

#### Proposed
```json
{

    "description": "Are you <em>{full_name}<em>?",
    "description_values": {
        "full_name": [
            {
                 "filter": "format_household_name",
                 "filter_args": [
                     {
                         "source": "answers",
                         "value": "first-name"
                     },
                     {
                         "source": "answers",
                         "value": "middle-names"
                     },
                     {
                         "source": "answers",
                         "value": "last-name"
                     }
                 ]
            }
        ]
    }
}
```

## format_household_name_possessive

**Note:** This filter should not add the `'s` in languages that don't have possessive nouns e.g. Welsh.

#### Current
```json
{
    "description": "What is {{[answers['first-name'][group_instance], answers['last-name'][group_instance]] | format_household_name_possessive }} date of birth?"
}
```

#### Proposed
```json
{

    "description": "What is {full_name_possessive} date of birth?",
    "description_values": {
        "full_name_possessive": [
            {
                 "filter": "format_household_name_possessive",
                 "filter_args": [
                     {
                         "source": "answers",
                         "value": "first-name"
                     },
                     {
                         "source": "answers",
                         "value": "middle-names"
                     },
                     {
                         "source": "answers",
                         "value": "last-name"
                     }
                 ]
            }
        ]
    }
}
```

## format_unordered_list

**Note:** The input to this filter is a list.

#### Current
```json
{
    "description": "{{ answers['pay-pattern-frequency-answer']|format_unordered_list }}"
}
```

#### Proposed
```json
{

    "description": "{list_of_pay_patterns}",
    "description_values": {
        "list_of_pay_patterns": [
            {
                 "filter": "format_unordered_list",
                 "filter_args": [
                     {
                         "source": "answers",
                         "value": "pay-pattern-frequency-answer"
                     }
                 ]
            }
        ]
    }
}
```

## format_unordered_list_missing_items

**Note:** The input to this filter is two lists.

#### Current
```json
{
    "description": "{{ format_unordered_list_missing_items(['Online ordering or reservation/booking', 'Description of goods or services, price lists', 'Order tracking', 'The possibility for visitors to customise or design the goods or services online', 'Personalised content for regular/repeat visitors', 'Links or references to this business’ social media profiles'], answers['answer1836']) }}"
}
```

#### Proposed
```json
{

    "description": "{list_of_missing_items}",
    "description_values": {
        "list_of_missing_items": [
            {
                 "filter": "format_unordered_list_missing_items",
                 "filter_args": [
                     {
                         "value": ["Online ordering or reservation/booking", "Description of goods or services, price lists", "Order tracking", "The possibility for visitors to customise or design the goods or services online", "Personalised content for regular/repeat visitors", "Links or references to this business’ social media profiles"]
                     },
                     {
                         "source": "answers",
                         "value": "answer1836"
                     }
                 ]
            }
        ]
    }
}
```

## format_household_summary

**Note:** This filter would need to be used outside of a repeat so we know not to filter the list by `group_instance`.

#### Current
```json
{
    "description": "<h2 class='neptune'>Your household includes:</h2> {{ [answers['first-name'], answers['middle-names'], answers['last-name']]|format_household_summary }}"
}
```

#### Proposed
```json
{
    "description": "<h2 class='neptune'>Your household includes:</h2> {list_of_household_names}",
    "description_values": {
        "list_of_household_names": [
            {
                 "filter": "format_household_summary",
                 "filter_args": [
                     {
                         "source": "answers",
                         "value": "first-name"
                     },
                     {
                         "source": "answers",
                         "value": "middle-names"
                     },
                     {
                         "source": "answers",
                         "value": "last-name"
                     }
                 ]
            }
        ]
    }
}
```

## format_repeating_summary

We should rethink how we get the list of people rather than make this work in a Jinja filter (the proposed json doesn't quite work).

#### Current
```json
{
    "description": "{{ [[answers['primary-household-member-first-name'], answers['primary-household-member-last-name']], [answers['other-household-member-first-name'], answers['other-household-member-last-name']], [answers['student-household-member-first-name'], answers['student-household-member-last-name']]] | format_repeating_summary }}"
}
```

#### Proposed
```json
{
    "description": "{list_of_household_names}",
    "description_values": {
        "list_of_household_names": [
            {
                 "filter": "format_repeating_summary",
                 "filter_args": [
                     {
                         "source": "answers",
                         "value": [
                             "primary-household-member-first-name",
                             "primary-household-member-last-name"
                         ]
                     },
                     {
                         "source": "answers",
                         "value": [
                             "other-household-member-first-name",
                             "other-household-member-last-name"
                         ]
                     },
                     {
                         "source": "answers",
                         "value": [
                             "student-household-member-first-name",
                             "student-household-member-last-name"
                         ]
                     }
                 ]
            }
        ]
    }
}
```

## Worked examples

#### Original 

```json
{
    "type": "ConfirmationQuestion",
    "id": "confirm-dob-proxy",
    "questions": [{
        "id": "confirm-date-of-birth-proxy",
        "title": "{{[answers['first-name'][group_instance], answers['last-name'][group_instance]] | format_household_name}} is {{ calculate_years_difference (answers['date-of-birth-answer'][group_instance], 'now') }} old. Is this correct?",
        "type": "General",
        "answers": [{
            "id": "confirm-date-of-birth-answer-proxy",
            "mandatory": true,
            "options": [{
                    "label": "Yes, {{[answers['first-name'][group_instance], answers['last-name'][group_instance]] | format_household_name}} is {{ calculate_years_difference (answers['date-of-birth-answer'][group_instance], 'now') }} old",
                    "value": "Yes"
                },
                {
                    "label": "No, I need to change their date of birth",
                    "value": "No"
                }
            ],
            "type": "Radio"
        }]
    }],
    ...
}
```

#### Proposed

```json
{
    "type": "ConfirmationQuestion",
    "id": "confirm-dob-proxy",
    "questions": [{
        "id": "confirm-date-of-birth-proxy",
        "title": {
            "text": "{person_name} is {age_in_years} old. Is this correct?",
            "placeholders": [
                {
                    "placeholder": "person_name",
                    "transforms": [
                        {
                            "transform": "concatenate_list",
                            "arguments": {
                                "list": {
                                    "source": "answers",
                                    "identifier": ["first-name","last-name"]
                                },
                                "delimiter": " "
                            }
                        }
                    ]
                },
                {
                    "placeholder": "age_in_years",
                    "transforms": [
                        {
                            "transform": "calculate_years_difference",
                            "arguments": {
                                "first_date": {
                                    "source": "answers",
                                    "identifier": "date-of-birth-answer"
                                },
                                "second_date": {
                                    "value": "now"
                                }
                            }
                        }
                    ]
                }
            ]
        },
        "type": "General",
        "answers": [{
            "id": "confirm-date-of-birth-answer-proxy",
            "mandatory": true,
            "options": [{
                    "label": {
                        "text": "{person_name} is {age_in_years} old. Is this correct?",
                        "placeholders": [
                            {
                                "placeholder": "person_name",
                                "transforms": [
                                    {
                                        "transform": "concatenate_list",
                                        "arguments": {
                                            "list": {
                                                "source": "answers",
                                                "identifier": ["first-name","last-name"]
                                            },
                                            "delimiter": " "
                                        }
                                    }
                                ]
                            },
                            {
                                "placeholder": "age_in_years",
                                "transforms": [
                                    {
                                        "transform": "calculate_years_difference",
                                        "arguments": {
                                            "first_date": {
                                                "source": "answers",
                                                "identifier": "date-of-birth-answer"
                                            },
                                            "second_date": {
                                                "value": "now"
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    "value": "Yes"
                },
                {
                    "label": {
                        "text": "No, I need to change their date of birth"
                    },
                    "value": "No"
                }
            ],
            "type": "Radio"
        }]
    }],
    ...
}
```

- The repetition of placeholder resolution in the same block is rare
- Repetition of person name throughout the census - have one definition that gets re-used?