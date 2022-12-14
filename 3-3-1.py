import requests
import pandas as pd

pd.set_option('expand_frame_repr', False)
df = pd.read_csv('vacancies_dif_currencies.csv')

df['published'] = pd.to_datetime(df['published_at'], format='%Y-%m-%dT%H:%M:%S%z', utc=True)
date_sort = df.sort_values(by='published').reset_index()
months = list(date_sort.published.dt.strftime('%m/%Y').unique())

print(list(months))

min_date = date_sort.loc[0, 'published'] #.strftime('%d/%m/%Y'), format="%Y-%m-%dT%H:%M:%S%z".astype('datetime64[ns]')
max_date = date_sort['published'].iloc[-1] #.strftime('%d/%m/%Y')

a = df.groupby('salary_currency')['salary_currency'].count()
w = a[a > 5000].to_dict()
print(w)

months = ['01/2003', '02/2003', '03/2003', '04/2003', '05/2003', '06/2003', '07/2003', '08/2003', '09/2003', '10/2003', '11/2003', '12/2003', '01/2004', '02/2004', '03/2004', '04/2004', '05/2004', '06/2004', '07/2004', '08/2004', '09/2004', '10/2004', '11/2004', '12/2004', '01/2005', '02/2005', '03/2005', '04/2005', '05/2005', '06/2005', '07/2005', '08/2005', '09/2005', '10/2005', '11/2005', '12/2005', '01/2006', '02/2006', '03/2006', '04/2006', '05/2006', '06/2006', '07/2006', '08/2006', '09/2006', '10/2006', '11/2006', '12/2006', '01/2007', '02/2007', '03/2007', '04/2007', '05/2007', '06/2007', '07/2007', '08/2007', '09/2007', '10/2007', '11/2007', '12/2007', '01/2008', '02/2008', '03/2008', '04/2008', '05/2008', '06/2008', '07/2008', '08/2008', '09/2008', '10/2008', '11/2008', '12/2008', '01/2009', '02/2009', '03/2009', '04/2009', '05/2009', '06/2009', '07/2009', '08/2009', '09/2009', '10/2009', '11/2009', '12/2009', '01/2010', '02/2010', '03/2010', '04/2010', '05/2010', '06/2010', '07/2010', '08/2010', '09/2010', '10/2010', '11/2010', '12/2010', '01/2011', '02/2011', '03/2011', '04/2011', '05/2011', '06/2011', '07/2011', '08/2011', '09/2011', '10/2011', '11/2011', '12/2011', '01/2012', '02/2012', '03/2012', '04/2012', '05/2012', '06/2012', '07/2012', '08/2012', '09/2012', '10/2012', '11/2012', '12/2012', '01/2013', '02/2013', '03/2013', '04/2013', '05/2013', '06/2013', '07/2013', '08/2013', '09/2013', '10/2013', '11/2013', '12/2013', '01/2014', '02/2014', '03/2014', '04/2014', '05/2014', '06/2014', '07/2014', '08/2014', '09/2014', '10/2014', '11/2014', '12/2014', '01/2015', '02/2015', '03/2015', '04/2015', '05/2015', '06/2015', '07/2015', '08/2015', '09/2015', '10/2015', '11/2015', '12/2015', '01/2016', '02/2016', '03/2016', '04/2016', '05/2016', '06/2016', '07/2016', '08/2016', '09/2016', '10/2016', '11/2016', '12/2016', '01/2017', '02/2017', '03/2017', '04/2017', '05/2017', '06/2017', '07/2017', '08/2017', '09/2017', '10/2017', '11/2017', '12/2017', '01/2018', '02/2018', '03/2018', '04/2018', '05/2018', '06/2018', '07/2018', '08/2018', '09/2018', '10/2018', '11/2018', '12/2018', '01/2019', '02/2019', '03/2019', '04/2019', '05/2019', '06/2019', '07/2019', '08/2019', '09/2019', '10/2019', '11/2019', '12/2019', '01/2020', '02/2020', '03/2020', '04/2020', '05/2020', '06/2020', '07/2020', '08/2020', '09/2020', '10/2020', '12/2020', '01/2021', '02/2021', '03/2021', '04/2021', '05/2021', '06/2021', '07/2021', '08/2021', '09/2021', '10/2021', '11/2021', '12/2021', '01/2022', '02/2022', '03/2022', '04/2022', '05/2022', '06/2022', '07/2022']


b = ['BYR', 'EUR', 'KZT', 'UAH', 'USD']
data2 = pd.DataFrame(columns=['date'] + b)

for i in range(0, len(months)):
    url = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{months[i]}d=1'
    response = requests.get(url)
    currencies = pd.read_xml(response.text)
    currencies2 = currencies.loc[currencies['CharCode'].isin(['BYN'] + b)]

    BYR = float(currencies2.loc[currencies2['CharCode'].isin(['BYR', 'BYN'])]['Value'].values[0].replace(',', '.')) / \
          (currencies2.loc[currencies2['CharCode'].isin(['BYR', 'BYN'])]['Nominal'].values[0])
    EUR = float(currencies2.loc[currencies2['CharCode'] == 'EUR']['Value'].values[0].replace(',', '.')) / \
          (currencies2.loc[currencies2['CharCode'] == 'EUR']['Nominal'].values[0])
    KZT = float(currencies2.loc[currencies2['CharCode'] == 'KZT']['Value'].values[0].replace(',', '.')) / \
          (currencies2.loc[currencies2['CharCode'] == 'KZT']['Nominal'].values[0])
    UAH = float(currencies2.loc[currencies2['CharCode'] == 'UAH']['Value'].values[0].replace(',', '.')) / \
          (currencies2.loc[currencies2['CharCode'] == 'UAH']['Nominal'].values[0])
    USD = float(currencies2.loc[currencies2['CharCode'] == 'USD']['Value'].values[0].replace(',', '.')) / \
          (currencies2.loc[currencies2['CharCode'] == 'USD']['Nominal'].values[0])

    data2.loc[i] = [f'{months[i][3:]}-{months[i][:2]}', BYR, EUR, KZT, UAH, USD]


data2.to_csv('currencies.csv', index=False)
print(data2.head())
