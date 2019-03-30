from timeit import Timer
import numpy as np
import housing_sim.utils

def stopwatch(f, trials):
    def wrapper(*args, **kwargs):
        t = Timer(lambda : f(*args, **kwargs))
        return t.timeit(number=trials)
    return wrapper

number_rows = 360
data_row_format = {
    'date': np.datetime64('nat'),
    'month': 0,
    'principal': np.nan,
    'interest': np.nan,
    'total_principal': np.nan,
    'total_interest': np.nan,
    'balance': np.nan
}

# Test blank row allocations
trials = 1000

print('START: TRIALS={}'.format(trials))
print('================================')
print('Timed blank df by rows')
timed_blank_df_by_rows = stopwatch(housing_sim.utils.allocate_empty_df, trials)(number_rows, data_row_format)
print(timed_blank_df_by_rows)

