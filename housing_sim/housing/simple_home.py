import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

import housing_sim.utils
from housing_sim.housing.abstract_home import AbstractHome


class SimpleHome(AbstractHome):
    def __init__(self, *args, **kwargs):
        super(SimpleHome, self).__init__(*args, **kwargs)

    def get_data(self):
        """
        Get/Generate all the data

        Columns:
            'date': date
            'month': number of months into ownership period
            'home_value': expected home value
            'home_ownership_pct': % home owned
            'direct': direct costs - principal
            'indirect': indirect costs - insurance, tax, interest, one-time & recurring fees
            'total_direct': sum of direct costs from start
            'total_indirect': sum of indirect costs from start
        """
        if self.data is not None:
            return self.data.copy()

        # Setup
        self.data = housing_sim.utils.blank_monthly_df(self.start_date, self.ownership_period_months, self.base_row_format)
        self.mortgage_data = self.mortgage.get_data()
        assert self.data.shape[0] == self.mortgage_data.shape[0], "Housing data and mortgage data must have same number of rows."

        # Home value and ownership percentage
        num_rows = self.data.shape[0]
        appreciation_rates = np.full(num_rows, 1 + self.appreciation_rate/12)
        home_appreciation_factor = np.power(appreciation_rates, self.data['month'])
        self.data['home_value'] = self.purchase_price * home_appreciation_factor
        self.data['home_ownership_pct'] = self.mortgage.down_payment_pct + (1-self.mortgage.down_payment_pct)*self.mortgage_data['pct_paid']

        # Direct costs
        self.data['direct'] = self.mortgage_data['principal'].values
        self.data.at[0, 'direct'] = self.mortgage.home_purchase_price * self.mortgage.down_payment_pct

        ### Calculate Indirect costs ###
        self.indirect_cost_data = pd.DataFrame()

        # Homeowners insurance
        self.indirect_cost_data['homeowners_insurance'] = self.data['home_value'] * self.homeowners_insurance_rate/12

        # Property Taxes
        is_property_tax_month = self.data['date'].apply(lambda date: date.month == 1)
        self.indirect_cost_data['property_tax'] = self.data['home_value'] * is_property_tax_month * self.property_tax_rate
        # First year is prorated - # of months you owned the home in the previous calendar year
        first_payment_index = np.argmax(is_property_tax_month.to_numpy() == True)
        taxable_first_months = first_payment_index + 1
        self.indirect_cost_data.at[first_payment_index, 'property_tax'] *= taxable_first_months/12

        # Mortgage Interest
        self.indirect_cost_data['interest'] = self.mortgage_data['interest']

        # Fees
        self.indirect_cost_data['fees'] = 0.0
        closing_costs = self.closing_cost_rate * self.purchase_price
        title_insurance_cost = self.title_insurance_rate * self.purchase_price
        self.indirect_cost_data.at[0, 'fees'] = closing_costs + title_insurance_cost

        self.indirect_cost_data['total'] = self.indirect_cost_data['property_tax'] + \
                                           self.indirect_cost_data['homeowners_insurance'] + \
                                           self.indirect_cost_data['fees'] + \
                                           self.indirect_cost_data['interest']


        # Copy indirect data over to main df
        self.data['indirect'] = self.indirect_cost_data['total'].values

        ### Calculate rolling totals ###
        self.data['total_direct'] = self.data['direct'].expanding(min_periods=1).sum()
        self.data['total_indirect'] = self.data['indirect'].expanding(min_periods=1).sum()

        return self.data.copy()

    def get_indirect_cost_data(self):
        self.get_data()
        return self.indirect_cost_data.copy()
