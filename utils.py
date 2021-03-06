import os
import math
import pandas as pd
import numpy as np
import quandl
import constants
quandl.ApiConfig.api_key = constants.QUANDL_API_KEY

def get_quandl_code(area_category, area_code, indicator_code):
    return "ZILLOW/{area_category}{area_code}_{indicator_code}".format(
        area_category=area_category,
        area_code=area_code,
        indicator_code=indicator_code
    )

def _cached_quandl_filename(quandl_code, method, *args, **kwargs):
    quandl_code_component = quandl_code.replace('/','_')
    args_component = "_".join(str(arg) for arg in args)
    kwarg_key_order = sorted(kwargs.keys())
    kwarg_data = []
    for key in kwarg_key_order:
        kwarg_str = "{}_{}".format(key, kwargs[key])
        kwarg_data.append(kwarg_str)
    kwargs_component = "__".join(kwarg_data)

    filename_format = "{method}_{quandl_code}__{args}__{kwargs}.pickle"
    filename = filename_format.format(
        method=method,
        quandl_code=quandl_code_component,
        args=args_component,
        kwargs=kwargs_component
    )
    return os.path.join(constants.DATA_DIR, filename)

def cached_quandl_get(quandl_code, *args, **kwargs):
    # generate file name
    filename = _cached_quandl_filename(quandl_code, 'GET', *args, **kwargs)
    # read file if it exists
    if (os.path.exists(filename)):
        return pd.read_pickle(filename)
    # fetch data
    data = quandl.get(quandl_code, *args, **kwargs)
    # save data
    data.to_pickle(filename)
    # return data
    return data

def compare_areas(areas, area_category_code, indicator_code, args_iterable=(), kwargs_iterable={}):
    dataframes = []
    for area_name, area_code in areas.items():
        code = get_quandl_code(area_category_code, area_code, indicator_code)
        try:
            data = cached_quandl_get(code, *args_iterable, **kwargs_iterable)
            data = data.rename(columns={'Value': area_name})
            dataframes.append(data)
        except Exception:
            print('unable to fetch {}|{}'.format(area_name, area_code))
    return pd.concat(dataframes, axis=1)

def fit_to_array(single_or_iterable, desired_length):
    """
    Get a numpy array of the desired length by repeating/truncating either a single item or iterable of items

    Examples:
        >> fit_to_array(0, 4)
        np.array([0,0,0,0])

        >> fit_to_array([1,2,3], 7)
        np.array([1,2,3,1,2,3,1])
    """
    if not hasattr(single_or_iterable, '__iter__'):
        arr = np.array([single_or_iterable])
    else:
        arr = np.array(single_or_iterable)

    if len(arr) < desired_length:
        numberOfTilesNeeded = math.ceil(desired_length / float(len(arr)))
        arr = np.tile(arr, numberOfTilesNeeded)

    return arr[:desired_length]
