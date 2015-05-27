'''
Created on Nov 7, 2012

@author: onep

Run this test using machine$ python lab_clinic_reference/tests.py from command line
'''
from operator import attrgetter

from django.test import TestCase

from lis.core.lab_reference.utils import get_upper_range_days, get_lower_range_days

from ..models import GradingListItem


class ListItemTests(TestCase):

    def test_age_range_overlaps(self):
        # build a query ad group by the same parameters used to retrieve grading list items in
        # lab_grading.classes.grade_flag, gradingListItems is a list of 1 item from each group
        gradingListItems = GradingListItem.objects.raw('''SELECT *
                                                          FROM lab_clinic_reference_gradinglistitem
                                                          GROUP BY grading_list_id, test_code_id, gender, hiv_status, serum, fasting''')
        print '################# START - AGE ###########################'
        for item in gradingListItems:

            # For each item gradingListItems, we want to get all the rest in the same group
            if item.active:
                expanded_test_code_items = self.related_items(item)
                # sort the list by age_high in the grading list item, we know there is a change of boundary
                # when age_high changes or the quantifier changes
                sorted_by_upper_bound = sorted(expanded_test_code_items, key=attrgetter('age_high', 'grade'))
                upper_bound_days = get_upper_range_days(sorted_by_upper_bound[0].age_high, sorted_by_upper_bound[0].age_high_unit, sorted_by_upper_bound[0].age_high_quantifier)
                previous_ls = sorted_by_upper_bound[0]
                for ls in sorted_by_upper_bound:
                    # If he age group is the same between two consequtive items, i.e 1-99,1-99 then they mpst likely belong to the same groups
                    # and if the age quantifiers are different then there is a high possibility that there is an error with the entered
                    # quantifiers.
                    if self.inconsistent_quantifiers(previous_ls, ls):
                        # previous_ls = ls
                        # print str(ls.age_low) +' - '+str(ls.age_high)+' G='+str(ls.grade)
                        continue
                    # we'll use lab_reference.utils.get_upper_range_days to compare the boundaries
                    upper_bound_days_temp = get_upper_range_days(ls.age_high, ls.age_high_unit, ls.age_high_quantifier)
                    if  upper_bound_days != upper_bound_days_temp and \
                        previous_ls.dummy != True and ls.dummy != True:
                            upper_bound_days = upper_bound_days_temp
                            # when we encounter a change in boundary, we check for gaps.
                            self.check_no_age_gap(previous_ls, ls)
                            previous_ls = ls

    def test_value_range_overlaps(self):
        # build a query ad group by the same parameters used to retrieve grading list items in
        # lab_grading.classes.grade_flag, gradingListItems is a list of 1 item from each group
        gradingListItems = GradingListItem.objects.raw('''SELECT *
                                                          FROM lab_clinic_reference_gradinglistitem
                                                          GROUP BY grading_list_id, test_code_id, gender, hiv_status, serum, fasting''')
        print '################# START - VALUE ###########################'
        for item in gradingListItems:

            # For each item gradingListItems, we want to get all the rest in the same group
            if item.active:
                expanded_test_code_items = self.related_items(item)
                # sort the list by age_high in the grading list item, we know there is a change of boundary
                # when age_high changes or the quantifier changes
                sorted_by_upper_bound = sorted(expanded_test_code_items, key=attrgetter('age_high', 'grade'))
                # upper_bound_days = get_upper_range_days(sorted_by_upper_bound[0].age_high,sorted_by_upper_bound[0].age_high_unit,sorted_by_upper_bound[0].age_high_quantifier)
                previous_ls = None
                for ls in sorted_by_upper_bound:
                    # If he age group is the same between two consequtive items, i.e 1-99,1-99 then they mpst likely belong to the same groups
                    # and if the age quantifiers are different then there is a high possibility that there is an error with the entered
                    # quantifiers.
                    if self.in_same_age_groups(previous_ls, ls) and \
                        previous_ls.dummy != True and ls.dummy != True:
                            self.check_no_value_gap(previous_ls, ls)
                    previous_ls = ls

    def in_same_age_groups(self, previous, current):
        if not previous:
            return False
        if previous.grade == current.grade and previous.age_low == current.age_low \
           and previous.age_high == current.age_high:
                print '############################################'
                print 'POSSIBLE DUPLICATE GRADE between (' + str(previous) + '), ' + str(previous.age_low) + \
                        ' - ' + str(previous.age_high) + ', Grade:' + str(previous.grade) + \
                        ', Value Range:' + str(previous.value_low) + ' - ' + str(previous.value_high) + \
                        ' and (' + str(current) + '), ' + str(current.age_low) + ' - ' + str(current.age_high) + \
                        ', Grade:' + str(current.grade) + ', Value Range:' + str(current.value_low) + 'L - ' + \
                        str(current.value_high) + 'H'
                return False
        elif current.grade > previous.grade:
            return True
        else:
            return False

    def check_no_value_gap(self, previous, current):
        down = previous.value_low > current.value_low
        up = previous.value_low < current.value_low
        addable = (previous.value_low != None) and (previous.value_high != None)\
                     and (current.value_low != None) and (current.value_high != None)
        if not addable:
            self.value_print_no_value(previous, current)
            return
        # self.assertFalse(down == up)
        if down == up:
            self.value_print_swapped(previous, current)
        if down and (previous.value_low - current.value_high) == 0:
            if previous.value_low_quantifier.strip(' \t\n\r') == '>' and current.age_high_quantifier.strip(' \t\n\r') == '<=':
                pass
            elif previous.age_low_quantifier.strip(' \t\n\r') == '>=' and current.age_high_quantifier.strip(' \t\n\r') == '<':
                pass
            else:
                self.value_print_overlap(previous, current)
        if down and (previous.value_low - current.value_high) != 0:
            self.value_print_overlap(previous, current)
        if up and (current.value_low - previous.value_high) == 0:
            if previous.value_high_quantifier.strip(' \t\n\r') == '<' and current.age_low_quantifier.strip(' \t\n\r') == '>=':
                pass
            elif previous.age_high_quantifier.strip(' \t\n\r') == '<=' and current.age_high_quantifier.strip(' \t\n\r') == '>':
                pass
            else:
                self.value_print_overlap(previous, current)
        if up and (current.value_low - previous.value_high) != 0:
            self.value_print_overlap(previous, current)

    def check_no_age_gap(self, previous, current):
        allowed_lower = ['>', '>=']
        allowed_upper = ['<', '<=']
        if previous.age_high_quantifier.strip(' \t\n\r') not in allowed_upper:
            raise TypeError('Invalid comparison operator. Was expecting {0}, Got {1}'.format(allowed_lower, current.age_low_quantifier))
        if current.age_low_quantifier.strip(' \t\n\r') not in allowed_lower:
            raise TypeError('Invalid comparison operator. Was expecting {0}, Got {1}'.format(allowed_upper, previous.age_high_quantifier))
        # pdb.set_trace()
        difference = get_lower_range_days(current.age_low, current.age_low_unit) - get_upper_range_days(previous.age_high, previous.age_high_unit, previous.age_high_quantifier)
        if difference == 0:
            # If the difference between boundaries is zero e.g 1-99 D, 99-200 D, then only the following combinations
            # of quantifiers will ensure no gap
            if previous.age_high_quantifier.strip(' \t\n\r') == '<' and current.age_low_quantifier.strip(' \t\n\r') == '>=':
                pass
            elif previous.age_high_quantifier.strip(' \t\n\r') == '<=' and current.age_low_quantifier.strip(' \t\n\r') == '>':
                pass
            else:
                self.age_print_overlap(previous, current, difference)
        elif difference == 1:
            # If the difference between boundaries is one e.g 1-99 D, 100-200 D, then only the following combinations
            # of quantifiers will ensure no gap
            if previous.age_high_quantifier.strip(' \t\n\r') == '<=' and current.age_low_quantifier.strip(' \t\n\r') == '>=':
                pass
            else:
                self.age_print_overlap(previous, current, difference)
        else:
            self.age_print_overlap(previous, current, difference)
        if previous:
#            print 'change of boundary , PREV:'+str(previous.age_high_quantifier)+' G='+str(previous.grade)+\
#                    ' Unit:'+str(previous.age_high_unit)+' ,CURR:'+str(current.age_low_quantifier)+\
#                    ' G='+str(current.grade)+' Unit:'+str(current.age_low_unit)+' DIFFERENCE='+str(difference)
            pass
        else:
            # print 'PREVIOUS is None'
            pass

    def inconsistent_quantifiers(self, previous_ls, ls):
        if get_upper_range_days(previous_ls.age_high, previous_ls.age_high_unit, previous_ls.age_high_quantifier) == \
            get_upper_range_days(ls.age_high, ls.age_high_unit, previous_ls.age_high_quantifier) and \
            get_lower_range_days(previous_ls.age_high, previous_ls.age_high_unit) == \
            get_lower_range_days(ls.age_high, ls.age_high_unit):
                if previous_ls.age_high_quantifier != ls.age_high_quantifier or \
                    previous_ls.age_low_quantifier != ls.age_low_quantifier:
                        self.age_print_duplicate_grade(previous_ls, ls)
                        return True
        return False

    def related_items(self, list_items_sample):
        items = list(GradingListItem.objects.filter(grading_list_id=list_items_sample.grading_list_id,
                                                test_code_id=list_items_sample.test_code_id,
                                                gender=list_items_sample.gender,
                                                hiv_status=list_items_sample.hiv_status,
                                                serum=list_items_sample.serum,
                                                fasting=list_items_sample.fasting))
        return items

    def value_print_no_value(self, previous, current):
        print '############################################'
        print 'NO VALUE set on (' + str(previous) + '), ' + str(previous.age_low) + \
                    ' - ' + str(previous.age_high) + ', Grade:' + str(previous.grade) + \
                    ', Value Range:' + str(previous.value_low) + 'L - ' + str(previous.value_high) + 'H' + \
                    ' and (' + str(current) + '), ' + str(current.age_low) + ' - ' + str(current.age_high) + \
                    ', Grade:' + str(current.grade) + ', Value Range:' + str(current.value_low) + 'L - ' + \
                    str(current.value_high) + 'H'

    def value_print_swapped(self, previous, current):
        print '############################################'
        print 'SWAPPED VALUE_LOW and VALUE_HIGH in one of (' + str(previous) + '), ' + str(previous.age_low) + \
                    ' - ' + str(previous.age_high) + ', Grade:' + str(previous.grade) + \
                    ' ,Low Quantifier:' + str(previous.value_low_quantifier) + \
                    ' ,High Quantifier:' + str(previous.value_high_quantifier) + \
                    ', Value Range:' + str(previous.value_low) + 'L - ' + str(previous.value_high) + 'H '\
                    ' and (' + str(current) + '), ' + str(current.age_low) + ' - ' + str(current.age_high) + \
                    ', Grade:' + str(current.grade) + ', Value Range:' + str(current.value_low) + 'L - ' + \
                    str(current.value_high) + 'H ,Low Quantifier:' + str(previous.value_low_quantifier) + \
                    ' ,High Quantifier:' + str(previous.value_high_quantifier)

    def value_print_overlap(self, previous, current):
        print '############################################'
        print 'POSSIBLE GAP/OVERLAP GRADE between (' + str(previous) + '), ' + str(previous.age_low) + \
                ' - ' + str(previous.age_high) + ', Grade:' + str(previous.grade) + \
                ' ,Low Quantifier:' + str(previous.value_low_quantifier) + \
                ' ,High Quantifier:' + str(previous.value_high_quantifier) + \
                ', Value Range:' + str(previous.value_low) + 'L - ' + str(previous.value_high) + 'H' + \
                ' and (' + str(current) + '), ' + str(current.age_low) + ' - ' + str(current.age_high) + \
                ', Grade:' + str(current.grade) + ', Value Range:' + str(current.value_low) + 'L - ' + \
                str(current.value_high) + 'H ,Low Quantifier:' + str(previous.value_low_quantifier) + \
                ' ,High Quantifier:' + str(previous.value_high_quantifier) + \
                ' ,Overlap/Gap Value = ' + str(previous.value_low - current.value_high)

    def age_print_overlap(self, previous, current, difference):
        print '############################################'
        print 'A POSSIBLE GAP/OVERLAP ENCOUNTERED between (' + str(previous) + '), ' + str(previous.age_low) + \
                ' - ' + str(previous.age_high) + ', Unit:' + str(previous.age_high_unit) + \
                ', high_quantifier:' + str(previous.age_high_quantifier) + ' Serum:' + str(previous.serum) + \
                ' and (' + str(current) + '), ' + str(current.age_low) + ' - ' + str(current.age_high) + \
                ', Unit:' + str(current.age_high_unit) + ', low_quantifier:' + str(current.age_low_quantifier) + \
                ' Serum:' + str(current.serum) + ' Difference:' + str(difference)

    def age_print_duplicate_grade(self, previous_ls, ls):
        print '############################################'
        print 'POSSIBLE INCONSISTENCY IN QUANTIFIERS between (' + str(previous_ls) + '), ' + str(previous_ls.age_low) + \
        ' - ' + str(previous_ls.age_high) + ', Unit:' + str(previous_ls.age_high_unit) + ', Grade:' + str(previous_ls.grade) + \
        ', low_quantifier:' + str(previous_ls.age_low_quantifier) + ', high_quantifier:' + str(previous_ls.age_high_quantifier) + \
        ' and (' + str(ls) + '), ' + str(ls.age_low) + ' - ' + str(ls.age_high) + ', Unit:' + str(ls.age_high_unit) + \
        ', Grade:' + str(ls.grade) + ', low_quantifier:' + str(ls.age_low_quantifier) + ', high_quantifier:' + str(ls.age_high_quantifier)
