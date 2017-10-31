

class TimepointSelector:

    """Given a list of timepoints and number of desired visits, the timepoint
    selector picks timepoint datetime. e.g

    1. timepoints = [2017-9-3, 2017-9-4, 2017-9-5],
        number of visit = 1
       the selector will self.selected_timepoints = [2017-9-3].

    2. timepoints = [2017-9-3, 2017-9-4, 2017-9-5, 2017-9-6, 2017-9-4, 2017-9-7
        ], number of visit = 2
        the selector will self.selected_timepoints = [2017-9-3, 2017-9-6].

    3. timepoints = [2017-9-3, 2017-9-4, 2017-9-5, 2017-9-6],
        number of visit = 1
       the selector will self.selected_timepoints = [
       2017-9-3, 2017-9-4, 2017-9-5, 2017-9-6].
    """

    def __init__(self, workdays=None, number_of_visits=None):
        self.selected_timepoints = []
        self.workdays = workdays
        if number_of_visits == 1:
            self.selected_timepoints.append(workdays[0])
        elif number_of_visits == 2:
            self.selected_timepoints.append(workdays[0])
            self.selected_timepoints.append(self.get_middle_workday())
        else:
            divisible = int(len(workdays) / number_of_visits)
            divisible = divisible - 1
            for i in range(divisible):
                print(i)
                if i == 0:
                    self.selected_timepoints.append(workdays[i])
                else:
                    index = divisible * i
                    self.selected_timepoints.append(workdays[index])

    def get_middle_workday(self):

        def is_odd(days=None):
            return True if not days % 2 == 0 else False

        number_of_days = len(self.workdays)
        if is_odd(number_of_days):
            number_of_days = int((number_of_days / 2) + 0.5)
        else:
            number_of_days = int((number_of_days / 2)) + 1
        return self.workdays[number_of_days]
