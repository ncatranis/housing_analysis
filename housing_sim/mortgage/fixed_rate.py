import numpy as np

import housing_sim.utils
from .abstract_mortgage import AbstractMortgage

class SimpleFixedRateMortgage(AbstractMortgage):
    """
    A type of mortgage where each month's payment is exactly the same over the life of the mortgage
    """

    def __init__(self, yearly_interest_rate, *args, **kwargs):
        super(SimpleFixedRateMortgage, self).__init__(*args, **kwargs)
        self.interest_rate = yearly_interest_rate

    def get_data(self):
        """
        Get/Generate all the data

        Columns:
            'date'
            'month'
            'principal'
            'interest'
            'total_principal'
            'total_interest'
            'balance'
            'pct_paid'
        """
        if self.data is not None:
            return self.data

        self.data = housing_sim.utils.blank_monthly_df(self.start_date, self.loan_period_months, self.base_row_format)
        rate = self.interest_rate / 12
        calc_principal = lambda month: np.ppmt(rate, month+1, self.loan_period_months, self.loan_amount)
        calc_interest = lambda month: np.ipmt(rate, month+1, self.loan_period_months, self.loan_amount)
        self.data['principal'] = self.data['month'].apply(calc_principal) * -1
        self.data['interest'] = self.data['month'].apply(calc_interest) * -1
        self.data['total_principal'] = self.data['principal'].expanding(min_periods=1).sum()
        self.data['total_interest'] = self.data['interest'].expanding(min_periods=1).sum()
        self.data['balance'] = self.loan_amount - self.data['total_principal']
        self.data['pct_paid'] = 1 - (self.data.balance / self.loan_amount)
        return self.data

    @property
    def fixed_monthly_payment_size(self):
        """
        The fixed payment is equal to the following formula:

        rP * (1+r)^N / ((1+r)^N - 1)

        P = L[c(1 + c)n]/[(1 + c)n - 1]

        r: the monthly interest rate
        P: the loan principal
        N: the number of months
        """
        r = self.interest_rate / 12
        P = self.loan_amount
        N = self.loan_period_months

        top = r * pow(1 + r, N)
        bottom = pow(1 + r, N) - 1
        return max(0, P * top / bottom)
