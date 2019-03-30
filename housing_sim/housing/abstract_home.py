import numpy as np
from dateutil.relativedelta import relativedelta

class AbstractHome(object):
    def __init__(self, purchase_price, mortgage, start_date=None, num_months=None):
        """
        Create a Home object that handles paying a mortgage, taxes, and other costs

        Args:
            purchase_price (float): The price that the home was bought for
            mortgage (AbstractMortgage): The mortgage object associated with the home loan
            start_date (datetime): When the home was bought. If None, uses mortgage start date
            num_months (int): When to stop running calculations. If None, uses same period as mortgage

        Attributes:
            value (float): The current value of the home, assessed yearly
            homeowners_insurance_rate (float): yearly insurance rate as a percentage of home value, paid monthly
            property_tax_rate (float): yearly propery tax rate as a percentage of home value, paid every January
        """
        self.mortgage = mortgage
        self.purchase_price = purchase_price
        self.value = purchase_price  # assume initial value of home is equal to purchase price
        self.homeowners_insurance_rate = 0.01
        self.property_tax_rate = 0.02
        self.appreciation_rate = 0.02
        self.closing_cost_rate = 0.05
        self.title_insurance_rate = 0.01

        # Start date
        if start_date is not None:
            self.start_date = start_date
        else:
            self.start_date = mortgage.start_date
        # End date / Ownership Period
        if num_months is not None:
            self.ownership_period_months = num_months
        else:
            self.ownership_period_months = mortgage.loan_period_months
        self.end_date = self.start_date + relativedelta(months=self.ownership_period_months)

        self.base_row_format = {
            'date': np.datetime64('nat'),
            'month': 0,
            'home_value': np.nan,
            'home_ownership_pct': np.nan,
            'direct': np.nan,
            'indirect': np.nan,
            'total_direct': np.nan,
            'total_indirect': np.nan
        }

        self.data = None


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
        self.data = housing_sim.utils.blank_monthly_df(self.start_date, self.loan_period_months, self.base_row_format)
