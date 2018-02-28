from pyspark.sql.functions import lit, col, desc, countDistinct
from pyspark.sql import Window
import pyspark.sql.functions as F
from helpers import date_plus_x_days


def locale_on_date(data, date, topN, country_list=None, period=7):
    """ Gets the ratio of the top locales in each country over the last week.

    parameters:
        data: The main ping server
        date: The date to find the locale distribution
        country_list: The list to find look at in the analysis
        period: The number of days before looked at in the analyisis
        topN: The number of locales to get for each country. Only does the top N.

    output:
       dataframe with columns:
           ['country', 'start_date', 'submission_date_s3', 'locale', 'ratio_on_locale']
    """
    data_all = data.drop('country')\
        .select('submission_date_s3', 'client_id', 'locale',
                F.lit('All').alias('country'))

    if country_list is not None:
        data_countries = data.filter(F.col('country').isin(country_list))\
                    .select('submission_date_s3', 'client_id', 'locale', 'country')

        data_all = data_all.union(data_countries)

    begin = date_plus_x_days(date, -period)

    wau = data_all\
        .filter((col('submission_date_s3') <= date) & (col('submission_date_s3') > begin))\
        .groupBy('country')\
        .agg(countDistinct('client_id').alias('WAU'))\

    locale_wau = data_all\
        .filter((col('submission_date_s3') <= date) & (col('submission_date_s3') > begin))\
        .groupBy('country', 'locale')\
        .agg(countDistinct('client_id').alias('WAU_on_locale'))\
        .select(lit(begin).alias('start_date'), lit(date).alias('submission_date_s3'),
                'country', 'WAU_on_locale', 'locale')

    res = locale_wau.join(wau, 'country', how='left')\
        .select('start_date', 'submission_date_s3',
                'country', 'WAU_on_locale', 'locale', 'WAU')

    w = Window.partitionBy('country', 'submission_date_s3').orderBy(desc('WAU_on_locale'))
    return res.select('*', F.row_number().over(w).alias('rank'))\
            .filter(col('rank') <= topN)\
            .select('country', 'start_date', 'submission_date_s3', 'locale',
                    (col('WAU_on_locale') / col('WAU')).alias('ratio_on_locale'))
