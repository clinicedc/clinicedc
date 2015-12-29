from datetime import date, timedelta
"Test Cases Start-HEMOGLOBIN"

DAYS_TO_SUBTRACT_1 = 58
# # Adult and Pediartic>=57 days HIV POSETIVE-GRADE1
G1_TEST_1 = {'result_value': 8.444,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G1_TEST_2 = {'result_value': 8.459,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G1_TEST_3 = {'result_value': 10.044,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G1_TEST_4 = {'result_value': 10.059,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G1_TEST_5 = {'result_value': 9.459,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G1_TEST_6 = {'result_value': 11.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}

# Adult and Pediartic>=57 days HIV POSETIVE-GRADE2
G2_TEST_1 = {'result_value': 7.444,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G2_TEST_2 = {'result_value': 7.459,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G2_TEST_3 = {'result_value': 8.444,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G2_TEST_4 = {'result_value': 8.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G2_TEST_5 = {'result_value': 8.111,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G2_TEST_6 = {'result_value': 9.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}

# Adult and Pediartic>=57 days HIV POSETIVE-GRADE3
G3_TEST_1 = {'result_value': 6.444,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G3_TEST_2 = {'result_value': 6.559,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G3_TEST_3 = {'result_value': 7.444,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G3_TEST_4 = {'result_value': 7.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G3_TEST_5 = {'result_value': 7.111,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G3_TEST_6 = {'result_value': 8.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}

# Adult and Pediartic>=57 days HIV POSETIVE-GRADE4
G4_TEST_1 = {'result_value': 6.444,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G4_TEST_2 = {'result_value': 6.559,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G4_TEST_3 = {'result_value': 7.4444,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}
G4_TEST_4 = {'result_value': 5.0000,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'POS'}

# Adult and Pediartic>=57 days HIV NEGATIVE-GRADE1
G1_TEST_25 = {'result_value': 9.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G1_TEST_26 = {'result_value': 10.044,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G1_TEST_27 = {'result_value': 10.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G1_TEST_28 = {'result_value': 10.955,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G1_TEST_29 = {'result_value': 10.555,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G1_TEST_30 = {'result_value': 11.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}

# Adult and Pediartic>=57 days HIV NEGATIVE-GRADE2
G2_TEST_25 = {'result_value': 8.944,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G2_TEST_26 = {'result_value': 8.959,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G2_TEST_27 = {'result_value': 9.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G2_TEST_28 = {'result_value': 9.959,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G2_TEST_29 = {'result_value': 9.111,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G2_TEST_30 = {'result_value': 10.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}

# Adult and Pediartic>=57 days HIV NEGATIVE-GRADE3
G3_TEST_25 = {'result_value': 6.944,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G3_TEST_26 = {'result_value': 6.959,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G3_TEST_27 = {'result_value': 8.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G3_TEST_28 = {'result_value': 8.959,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G3_TEST_29 = {'result_value': 8.111,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G3_TEST_30 = {'result_value': 9.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}

# Adult and Pediartic>=57 days HIV NEGATIVE-GRADE4
G4_TEST_17 = {'result_value': 6.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G4_TEST_18 = {'result_value': 7.059,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G4_TEST_19 = {'result_value': 7.444,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}
G4_TEST_20 = {'result_value': 6.000,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_1),
             'gender': 'MF',
             'hiv_status': 'NEG'}

DAYS_TO_SUBTRACT_2 = 40
# Adult and Pediartic 36-56 days HIV POSETIVE/NEGATIVE-GRADE1 - TODO:ALSO HAVE TO TEST AGE RANGE
G1_TEST_7 = {'result_value': 8.444,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_8 = {'result_value': 8.455,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_9 = {'result_value': 9.444,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_10 = {'result_value': 9.455,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_11 = {'result_value': 9.111,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_12 = {'result_value': 10.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}

# Adult and Pediartic 36-56 days HIV POSETIVE/NEGATIVE-GRADE2
G2_TEST_7 = {'result_value': 6.944,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_8 = {'result_value': 7.044,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_9 = {'result_value': 8.444,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_10 = {'result_value': 8.455,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_11 = {'result_value': 8.111,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_12 = {'result_value': 9.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}

# Adult and Pediartic 36-56 days HIV POSETIVE/NEGATIVE-GRADE3
G3_TEST_7 = {'result_value': 5.944,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_8 = {'result_value': 6.044,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_9 = {'result_value': 6.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_10 = {'result_value': 6.955,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_11 = {'result_value': 6.911,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_12 = {'result_value': 7.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}

# Adult and Pediartic> 36-56 days HIV POSETIVE/NEGATIVE-GRADE4
G4_TEST_5 = {'result_value': 5.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G4_TEST_6 = {'result_value': 6.155,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G4_TEST_7 = {'result_value': 6.054,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G4_TEST_8 = {'result_value': 5.000,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_2),
             'gender': 'MF',
             'hiv_status': 'ANY'}

DAYS_TO_SUBTRACT_3 = 30
# Adult and Pediartic 22-35 days HIV POSETIVE/NEGATIVE-GRADE1 - TODO:ALSO HAVE TO TEST AGE RANGE
G1_TEST_13 = {'result_value': 9.444,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_14 = {'result_value': 9.459,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_15 = {'result_value': 10.544,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_16 = {'result_value': 10.551,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_17 = {'result_value': 9.777,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_18 = {'result_value': 11.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}

# Adult and Pediartic 22-35 days HIV POSETIVE/NEGATIVE-GRADE2
G2_TEST_13 = {'result_value': 7.914,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_14 = {'result_value': 8.044,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_15 = {'result_value': 9.444,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_16 = {'result_value': 9.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_17 = {'result_value': 9.111,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_18 = {'result_value': 10.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}

# Adult and Pediartic 22-35 days HIV POSETIVE/NEGATIVE-GRADE3
G3_TEST_13 = {'result_value': 6.944,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_14 = {'result_value': 7.044,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_15 = {'result_value': 7.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_16 = {'result_value': 7.959,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_17 = {'result_value': 7.511,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_18 = {'result_value': 8.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}

# Adult and Pediartic> 22-35 days HIV POSETIVE/NEGATIVE-GRADE4
G4_TEST_9 = {'result_value': 6.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G4_TEST_10 = {'result_value': 7.059,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G4_TEST_11 = {'result_value': 7.444,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G4_TEST_12 = {'result_value': 6.000,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_3),
             'gender': 'MF',
             'hiv_status': 'ANY'}

DAYS_TO_SUBTRACT_4 = 20
# Adult and Pediartic <= 21 days HIV POSETIVE/NEGATIVE-GRADE1 - TODO:ALSO HAVE TO TEST AGE RANGE
G1_TEST_19 = {'result_value': 11.944,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_20 = {'result_value': 11.959,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_21 = {'result_value': 13.044,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_22 = {'result_value': 13.055,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_23 = {'result_value': 12.777,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G1_TEST_24 = {'result_value': 13.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}

# Adult and Pediartic <= 21 days HIV POSETIVE/NEGATIVE-GRADE2
G2_TEST_19 = {'result_value': 9.944,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_20 = {'result_value': 9.955,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_21 = {'result_value': 11.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_22 = {'result_value': 11.959,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_23 = {'result_value': 10.111,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G2_TEST_24 = {'result_value': 12.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}

# Adult and Pediartic <= 21 days HIV POSETIVE/NEGATIVE-GRADE3
G3_TEST_19 = {'result_value': 8.944,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_20 = {'result_value': 8.955,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_21 = {'result_value': 9.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_22 = {'result_value': 9.959,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_23 = {'result_value': 9.511,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G3_TEST_24 = {'result_value': 10.459,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}

# Adult and Pediartic <= 21 days HIV POSETIVE/NEGATIVE-GRADE4
G4_TEST_13 = {'result_value': 8.944,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G4_TEST_14 = {'result_value': 9.159,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G4_TEST_15 = {'result_value': 9.544,  # FALSE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
G4_TEST_16 = {'result_value': 8.000,  # TRUE
             'test_code': 'HGB',
             'datetime_drawn': date.today(),
             'dob': date.today() - timedelta(days=DAYS_TO_SUBTRACT_4),
             'gender': 'MF',
             'hiv_status': 'ANY'}
"Test Cases End-HEMOGLOBIN"

# TRUE_G1_ASSERTIONS = [G1_TEST_2,G1_TEST_3,G1_TEST_5,G1_TEST_8,G1_TEST_9,G1_TEST_11,G1_TEST_14,G1_TEST_15,G1_TEST_17,G1_TEST_20,G1_TEST_21,G1_TEST_23]
# FALSE_G1_ASSERTIONS = [G1_TEST_1,G1_TEST_4, ,G1_TEST_7,G1_TEST_10,G1_TEST_12,G1_TEST_13,G1_TEST_16,G1_TEST_18,G1_TEST_19,G1_TEST_22,G1_TEST_24]
# TRUE_G2_ASSERTIONS = [G2_TEST_2,G2_TEST_3,G2_TEST_5,G2_TEST_8,G2_TEST_9,G2_TEST_11,G2_TEST_14,G2_TEST_15,G2_TEST_17,G2_TEST_20,G2_TEST_21,G2_TEST_23]
# FALSE_G2_ASSERTIONS = [G2_TEST_1,G2_TEST_4,G2_TEST_6,G2_TEST_7,G2_TEST_10,G2_TEST_12,G2_TEST_13,G2_TEST_16,G2_TEST_18,G2_TEST_19,G2_TEST_22,G2_TEST_24]
# TRUE_G3_ASSERTIONS = [G3_TEST_2,G3_TEST_3,G3_TEST_5,G3_TEST_8,G3_TEST_9,G3_TEST_11,G3_TEST_14,G3_TEST_15,G3_TEST_17,G3_TEST_20,G3_TEST_21,G3_TEST_23]
# FALSE_G3_ASSERTIONS = [G3_TEST_1,G3_TEST_4,G3_TEST_6,G3_TEST_7,G3_TEST_10,G3_TEST_12,G3_TEST_13,G3_TEST_16,G3_TEST_18,G3_TEST_19,G3_TEST_22,G3_TEST_24]
# TRUE_G4_ASSERTIONS = [G4_TEST_1,G4_TEST_4,G4_TEST_5,G4_TEST_8,G4_TEST_9,G4_TEST_12,G4_TEST_13,G4_TEST_16]
# FALSE_G4_ASSERTIONS = [G4_TEST_2,G4_TEST_3,G4_TEST_6,G4_TEST_7,G4_TEST_10,G4_TEST_11,G4_TEST_14,G4_TEST_15]

TRUE_G1_ASSERTIONS = [G1_TEST_2, G1_TEST_3, G1_TEST_5, G1_TEST_9, G1_TEST_8, G1_TEST_11 , G1_TEST_26, G1_TEST_27, G1_TEST_29, G1_TEST_14, G1_TEST_15, G1_TEST_17, G1_TEST_20, G1_TEST_21, G1_TEST_23]
FALSE_G1_ASSERTIONS = [G1_TEST_1, G1_TEST_4, G1_TEST_6, G1_TEST_10, G1_TEST_12, G1_TEST_7, G1_TEST_25, G1_TEST_28, G1_TEST_30, G1_TEST_13, G1_TEST_16, G1_TEST_18, G1_TEST_19, G1_TEST_22, G1_TEST_24]
TRUE_G2_ASSERTIONS = [G2_TEST_2, G2_TEST_3, G2_TEST_5, G2_TEST_8, G2_TEST_11, G2_TEST_9, G2_TEST_26, G2_TEST_27, G2_TEST_29, G2_TEST_14, G2_TEST_15, G2_TEST_17, G2_TEST_20, G2_TEST_21, G2_TEST_23]
FALSE_G2_ASSERTIONS = [G2_TEST_1, G2_TEST_4, G2_TEST_6, G2_TEST_10, G2_TEST_12, G2_TEST_7, G2_TEST_25, G2_TEST_28, G2_TEST_30, G2_TEST_13, G2_TEST_16, G2_TEST_18, G2_TEST_19, G2_TEST_22, G2_TEST_24]
TRUE_G3_ASSERTIONS = [G3_TEST_2, G3_TEST_3, G3_TEST_5, G3_TEST_11, G3_TEST_9, G3_TEST_26, G3_TEST_27, G3_TEST_29, G3_TEST_15, G3_TEST_17, G3_TEST_21, G3_TEST_23, G3_TEST_8, G3_TEST_14, G3_TEST_20]  #
FALSE_G3_ASSERTIONS = [G3_TEST_1, G3_TEST_4, G3_TEST_6, G3_TEST_7, G3_TEST_10, G3_TEST_12, G3_TEST_25, G3_TEST_28, G3_TEST_30, G3_TEST_13, G3_TEST_16, G3_TEST_18, G3_TEST_19, G3_TEST_22, G3_TEST_24]
TRUE_G4_ASSERTIONS = [G4_TEST_1, G4_TEST_4, G4_TEST_9, G4_TEST_5, G4_TEST_8, G4_TEST_17, G4_TEST_20, G4_TEST_12, G4_TEST_13, G4_TEST_16]
FALSE_G4_ASSERTIONS = [G4_TEST_2, G4_TEST_3, G4_TEST_7, G4_TEST_6, G4_TEST_18, G4_TEST_19, G4_TEST_10, G4_TEST_11, G4_TEST_14, G4_TEST_15]
