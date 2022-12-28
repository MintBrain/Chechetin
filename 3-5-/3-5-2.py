import math
import pandas as pd
import sqlite3


def get_salary(row):
    salary_from, salary_to, salary_currency, published_at = row.loc['salary_from'], row.loc['salary_to'], row.loc['salary_currency'], row.loc['published_at']
    currency_value = 0
    if salary_currency in ['BYN', 'BYR', 'EUR', 'KZT', 'UAH', 'USD']:
        salary_currency.replace('BYN', 'BYR')
        currency_value = cur.execute("SELECT * FROM currencies WHERE date == :published_at", {"published_at": published_at}).fetchone()[currencies_col_id[salary_currency]]
    elif salary_currency == 'RUR':
        currency_value = 1

    if math.isnan(salary_to) or math.isnan(salary_from):
        salary = salary_to if math.isnan(salary_from) else salary_from
    else:
        salary = math.floor((salary_from + salary_to) / 2)

    if math.isnan(salary):
        return salary

    return math.floor(salary * currency_value)


currencies_col_id = {"BYR": 1, "EUR": 2, "KZT": 3, "UAH": 4, "USD": 5}
df = pd.read_csv("../vacancies_dif_currencies.csv")
con = sqlite3.connect("currencies.sqlite")
cur = con.cursor()

df["published_at"] = df["published_at"].apply(lambda date: date[:7])
df['salary'] = df.apply(lambda x: get_salary(x), axis=1)
df.drop(columns=['salary_from', 'salary_to', 'salary_currency'], inplace=True)

connect = sqlite3.connect("vacancies_dif_currencies.sqlite")
cursor = con.cursor()
df.to_sql(name="vacancies_dif_currencies", con=connect, if_exists='replace', index=False)
connect.commit()
