from faker import Faker
from mage_ai.data_cleaner import column_type_detector
from mage_ai.data_cleaner.column_type_detector import (
    CATEGORY,
    CATEGORY_HIGH_CARDINALITY,
    DATETIME,
    EMAIL,
    MAXIMUM_WORD_LENGTH_FOR_CATEGORY_FEATURES,
    NUMBER,
    NUMBER_WITH_DECIMALS,
    PHONE_NUMBER,
    TEXT,
    TRUE_OR_FALSE,
    ZIP_CODE,
    get_mismatched_row_count,
    infer_column_types,
    REGEX_NUMBER,
)
from mage_ai.tests.base_test import TestCase
import pandas as pd
import numpy as np


class ColumnTypeDetectorTests(TestCase):
    def setUp(self):
        Faker.seed(42)
        self.fake = Faker()
        return super().setUp()

    def test_get_mismatched_row_count(self):
        df = pd.DataFrame(
            [
                [1, 'abc@xyz.com', '32132'],
                [2, 'abc2@xyz.com', '12345'],
                [3, 'test', '1234'],
                [4, 'abc@test.net', 'abcde'],
                [5, 'abc12345@', '54321'],
                [6, 'abcdef@123.com', '56789'],
            ],
            columns=['id', 'email', 'zip_code'],
        )
        count1 = get_mismatched_row_count(df['id'], 'number')
        count2 = get_mismatched_row_count(df['email'], 'email')
        count3 = get_mismatched_row_count(df['zip_code'], 'zip_code')
        self.assertEqual(count1, 0)
        self.assertEqual(count2, 2)
        self.assertEqual(count3, 1)

    def test_number_pattern_matching(self):
        good_number_patterns = [
            '3123452',
            '23.234232',
            '-23,245,234.93',
            '.934',
            '-0.000002',
            '$ 0.043',
            '-€ 23,456,789.00092',
            '¥ 21345634',
            '- Rs   345.23423523',
            'CAD 2,345,234,345.23423',
            '234.23423423 $',
            '-8907987 CAD',
            '3239458734 元',
            '234,2342,2343.823034234%',
            '234.3433   %',
        ]
        bad_number_patterns = [
            'this is not a number',
            'NOTCURR 23423933',
            '0.000.00.000.000',
            '1-111-111-111',
            ',2343234203',
            'ksjh&A(*2jnkj&#$#$',
        ]

        for good in good_number_patterns:
            print(good)
            match = REGEX_NUMBER.match(good)
            self.assertIsNotNone(match)

        for bad in bad_number_patterns:
            match = REGEX_NUMBER.match(bad)
            self.assertIsNone(match)

    def test_infer_column_types(self):
        columns = [
            'true_or_false',
            'number_with_decimals',
            'category',
            'datetime',
            'text',
            'number',
            'number_with_dollars',
            'number_with_percentage',
            'zip_code',
            'zip_code_with_3_numbers',
            'invalid_zip_code',
            'email',
            'phone_number',
            'datetime_abnormal',
            'name',
        ]
        table = [
            [
                '1',
                '3',
                'male',
                '2020-1-1',
                '1.0',
                '1',
                3,
                '30%',
                '10128-1213',
                123,
                123,
                'fire@mage.ai',
                '123-456-7890',
                'May 4, 2021, 6:35 PM',
                self.fake.name(),
            ],
            [
                '1',
                '12.0',
                'female',
                '2020-07-13',
                ' '.join(['t' for i in range(MAXIMUM_WORD_LENGTH_FOR_CATEGORY_FEATURES + 1)]),
                '2',
                '€4',
                '12.32%',
                12345,
                1234,
                1234,
                'mage@fire.com',
                '(123) 456-7890',
                'Feb 17, 2021, 2:57 PM',
                self.fake.name(),
            ],
            [
                '1',
                '0',
                'machine',
                '2020-06-25 01:02',
                ' '.join(['t' for i in range(MAXIMUM_WORD_LENGTH_FOR_CATEGORY_FEATURES + 1)]),
                '3',
                '¥5,000',
                '50%',
                '12345',
                12345,
                12345,
                'fire_mage@mage.com',
                '1234567890',
                'Feb 18, 2021, 2:57 PM',
                self.fake.name(),
            ],
            [
                0,
                '40.7',
                'mutant',
                '2020-12-25 01:02:03',
                ' '.join(['t' for i in range(MAXIMUM_WORD_LENGTH_FOR_CATEGORY_FEATURES + 1)]),
                '4',
                'Rs 5,000.01',
                '20%',
                '12345',
                12345,
                123456,
                'mage-fire@mage.ai',
                '1234567',
                'Feb 19, 2021, 2:57 PM',
                self.fake.name(),
            ],
            [
                0,
                '40.7',
                'alien',
                '2020-12-25T01:02:03.000Z',
                ' '.join(['t' for i in range(MAXIMUM_WORD_LENGTH_FOR_CATEGORY_FEATURES + 1)]),
                '4',
                '-10128,121.3123元',
                '18%',
                '01234',
                12345,
                12,
                'fire+1@mage.ai',
                '(123)456-7890',
                'Feb 20, 2021, 2:57 PM',
                self.fake.name(),
            ],
        ]
        date_formats = [
            '01/1/2019',
            '1/1/2019',
            '1/21/2019',
            '11/1/2019',
            '2020/01/1',
            '2020/1/01',
            '2020/1/1',
            'Pending',
        ]

        for date_format in date_formats:
            table.append(
                [
                    0,
                    '40.7',
                    'mutant',
                    date_format,
                    self.fake.text(),
                    4,
                    '$5,000.01',
                    '15.32%',
                    '01234',
                    12345,
                    12,
                    'fire+1@mage.ai',
                    '(123)456-7890',
                    'Feb 18, 2021, 2:57 PM',
                    self.fake.name(),
                ]
            )

        df = pd.DataFrame(table, columns=columns)
        column_types = infer_column_types(df)

        self.assertEqual(
            column_types,
            {
                'true_or_false': TRUE_OR_FALSE,
                'number_with_decimals': NUMBER_WITH_DECIMALS,
                'category': CATEGORY,
                'datetime': DATETIME,
                'text': TEXT,
                'number': NUMBER,
                'number_with_dollars': NUMBER_WITH_DECIMALS,
                'number_with_percentage': NUMBER_WITH_DECIMALS,
                'zip_code': ZIP_CODE,
                'zip_code_with_3_numbers': ZIP_CODE,
                'invalid_zip_code': NUMBER,
                'email': EMAIL,
                'phone_number': PHONE_NUMBER,
                'datetime_abnormal': DATETIME,
                'name': TEXT,
            },
        )

    def test_phone_number_recognition(self):
        df = pd.DataFrame(
            dict(
                phone_num=[self.fake.phone_number() for _ in range(6)],
                str_int_phone_nums=[
                    '9999999999',
                    '12345678909',
                    '918328328322',
                    '33459830234',
                    '8234592345',
                    '23439433343',
                ],
                not_phone_nums=[
                    '99999',
                    '12349',
                    '918328328322',
                    '33430234',
                    '8234592345',
                    '23439433343',
                ],
                int_phone_nums=[
                    9999999999,
                    12345678909,
                    918328328322,
                    33459830234,
                    8234592345,
                    23439433343,
                ],
                float_phone_nums=[
                    9999999999,
                    np.nan,
                    918328328322.0,
                    33459830234,
                    8234592345,
                    np.nan,
                ],
                not_float_phone_nums=[
                    9999999999.00234233,
                    np.nan,
                    918328328322.0,
                    33459830234.234,
                    8234592345,
                    np.nan,
                ],
            )
        )
        ctypes = infer_column_types(df)
        expected_ctypes = dict(
            phone_num='phone_number',
            str_int_phone_nums='phone_number',
            not_phone_nums='number',
            int_phone_nums='phone_number',
            float_phone_nums='phone_number',
            not_float_phone_nums='number_with_decimals',
        )
        self.assertEquals(ctypes, expected_ctypes)
