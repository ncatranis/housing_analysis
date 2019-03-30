import numpy as np
from dateutil.relativedelta import relativedelta

class AbstractMortgage(object):
    """
    Sets the standard for Mortgage data implementations to ensure it is all in a common format

    Common Attributes:
        start_date (datetime.date): the start date
        end_date (datetime.date): the anticipated end date
        loan_period_months (int): the number of months for the mortgage (e.g. 360)

        home_purchase_price (float): price of the home
        down_payment_pct (float): down payment as decimal percentage (e.g. 0.20)
        down_payment_amount (float): down payment in dollars (e.g. 50,000.00)

        loan_amount (float): initial size of the loan
        balance (float): remaining principal on the loan

    """

    def __init__(self, home_purchase_price, down_payment_pct, loan_start_date, loan_period_months):
        """
        Common data included in all mortgages

        Args:
            home_purchase_price (float): price of the home
            down_payment_pct (float): the down payment percentage
            loan_start_date (datetime.date): the start date of the mortgage
            loan_period_months (int): the length of the loan in months
        """
        self.start_date = loan_start_date
        self.end_date = loan_start_date + relativedelta(months=loan_period_months)
        self.loan_period_months = loan_period_months
        self.home_purchase_price = home_purchase_price
        self.down_payment_pct = down_payment_pct
        self.loan_amount = home_purchase_price * (1 - down_payment_pct)
        self.balance = self.loan_amount

        self.base_row_format = {
            'date': np.datetime64('nat'),
            'month': 0,
            'principal': np.nan,
            'interest': np.nan,
            'total_principal': np.nan,
            'total_interest': np.nan,
            'balance': np.nan,
            'pct_paid': np.nan
        }

        self.data = None

    def get_data(self):
        pass

    @property
    def is_paid(self):
        return self.balance < 0.01
