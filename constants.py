import secrets # python file with api keys as variables, see below

DATA_DIR = ".data" # where to store all pickle data
QUANDL_API_KEY = secrets.QUANDL_API_KEY # I save this info in a separate file that doesn't get committed

AREA_STATE = 'S'
AREA_COUNTY = 'CO'
AREA_METRO = 'M'
AREA_CITY = 'C'
AREA_NEIGHBORHOOD = 'N'
AREA_ZIPCODE = 'Z'

AUSTIN_METRO = 31
TRAVIS_COUNTY= 3148
