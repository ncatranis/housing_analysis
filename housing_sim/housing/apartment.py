import numpy as np
from dateutil.relativedelta import relativedelta

import housing_sim.utils

class Apartment(object):
    def __init__(self, base_rent, start_date, rent_period_months):
        self.start_date = start_date
        self.end_date = start_date + relativedelta(months=rent_period_months)
        self.rent_period_months = rent_period_months
        self.base_rent = base_rent
        self.yearly_increase_rate = 0.02
        self.base_row_format = {
            'date': np.datetime64('nat'),
            'month': 0,
            'rent': np.nan,
            'total_rent': np.nan,
        }

        self.data = None

    def get_data(self):
        if self.data is not None:
            return self.data.copy()
        self.data = housing_sim.utils.blank_monthly_df(self.start_date, self.rent_period_months, self.base_row_format)

        # Calculate increases in rent year-over-year
        years_passed = np.arange(0, self.rent_period_months/12)
        rent_increase_factor = np.power(1 + self.yearly_increase_rate, years_passed)
        # Convert yearly data into monthly data
        rent_increase_factor = rent_increase_factor.repeat(12)
        # Get rent for all months
        self.data['rent'] = self.base_rent * rent_increase_factor

        #Total rent
        self.data['total_rent'] = self.data['rent'].expanding(min_periods=1).sum()

        return self.data.copy()
