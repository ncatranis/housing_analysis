import numpy as np
import math
from dateutil.relativedelta import relativedelta

import housing_sim.utils
import utils
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

class DownPayableFixedRateMortgage(SimpleFixedRateMortgage):
    """
    Fixed rate mortgage with a fixed amount due each month, but can be paid off early
    """

    def __init__(self, yearly_interest_rate, home_purchase_price, down_payment_pct, loan_start_date, loan_period_months, extra_payment=0):
        """
        Args:
            yearly_interest_rate (float): interest rate as a decimal, e.g. 0.04
            home_purchase_price (float): price of the home
            down_payment_pct (float): the down payment percentage
            loan_start_date (datetime.date): the start date of the mortgage
            loan_period_months (int): the length of the loan in months
            extra_payment (float or iterable of floats): extra payment to make towards principal each month, e.g. 500 or [100, 200, ...]
                note on iterable arguments:
                    When paying down the mortgage early, it may be difficult to know the exact number of months where payment is required.
                    * if iterable is too short, it will be repeated
                    * if iterable is too long, payments after balance < 0 will not be applied.
        """
        super(DownPayableFixedRateMortgage, self).__init__(yearly_interest_rate, home_purchase_price, down_payment_pct, loan_start_date, loan_period_months)
        self.interest_rate = yearly_interest_rate
        self.extra_payment = utils.fit_to_array(extra_payment, loan_period_months)

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
        row_format = self.base_row_format.copy()
        row_format['extra_principal'] = np.nan

        self.data = housing_sim.utils.blank_monthly_df(self.start_date, self.loan_period_months, row_format)
        self._amortize()
        self.data['total_principal'] = self.data['principal'].expanding(min_periods=1).sum()
        self.data['total_extra_principal'] = self.data['extra_principal'].expanding(min_periods=1).sum()
        self.data['total_interest'] = self.data['interest'].expanding(min_periods=1).sum()
        self.data['balance'] = self.loan_amount - self.data['total_principal']
        self.data['pct_paid'] = 1 - (self.data['balance'] / self.loan_amount)
        return self.data


    def _amortize(self):
        payment = self.fixed_monthly_payment_size
        month = 0
        monthly_interest_rate = self.interest_rate/12

        while month < self.loan_period_months:
            if not self.is_paid:
                # Get the (principal, interest) components for the next payment after months_passed
                interest = monthly_interest_rate * self.balance
                payment = min(payment, self.balance + interest)
                principal = payment - interest

                # Adjust for extra principal
                extra_principal = min(self.extra_payment[month], self.balance - principal)
                self.balance = self.balance - principal - extra_principal
            else:
                # Mortgage is paid off early
                interest = 0
                payment = 0,
                principal = 0
                extra_principal = 0

            # Add data point
            self.data.at[month, 'date'] = self.start_date + relativedelta(months=month)
            self.data.at[month, 'month'] = month
            self.data.at[month, 'principal'] = principal
            self.data.at[month, 'extra_principal'] = extra_principal
            self.data.at[month, 'interest'] = interest
            self.data.at[month, 'balance'] = self.balance

            # Increment for next iteration
            month += 1
