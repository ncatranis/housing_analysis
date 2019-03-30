import pandas as pd
from dateutil.relativedelta import relativedelta

# Utility functions
def months_passed(stop, start):
    """
    Calculates the total number of months passed from start -> stop
    """
    years = relativedelta(stop, start).years
    months_in_year = relativedelta(stop, start).months
    return months_in_year + years * 12


def allocate_empty_df(number_rows, blank_row_format):
    """
    Generates an empty dataframe of {number_rows} size with each row containing {blank_row_format}
    as the initial state.

    We use this because editing a row is faster than appending a row.

    Args:
        number_rows (int): The number of rows in the df
        blank_row_format(dict): mapping of column names to default values of each row
            example:
            {
                'my_float_data': np.nan # 'nan' stands for 'not a number' and means undefined
                'my_integer_data': 0, # nan doesn't exist for integer types, so just use a zero
                'my_date_data': np.datetime64('nat'), # 'nat' means 'not a time' and is the datetime equivalent of np.nan
            }

    Returns: an empty dataframe
    """
    index = range(0, number_rows)
    blank_data = {col: [val for _ in index] for col, val in blank_row_format.items()}
    return pd.DataFrame(data=blank_data)

def blank_monthly_df(start_date, number_rows, blank_row_format, date_colname='date', month_colname='month'):
    """
    Helper method to call allocate_empty_df, but pre-populate 'date' and 'month' rows from start -> end

    :param start_date: Start datetime (inclusive)
    :param number_rows: Number of rows (months)
    :param blank_row_format: same as in allocate_empty_df
    :param date_colname: the name of the date column that holds prepopulated datetimes
    :param month_colname: the name of the months column that holds prepopulated ints

    :return: empty dataframe with prepopulated date and month rows
    """
    df = allocate_empty_df(number_rows, blank_row_format)
    df[date_colname] = pd.date_range(start_date, periods=number_rows, freq='MS')
    df[month_colname] = range(0, number_rows)
    return df
