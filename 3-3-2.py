import math
import os
import pandas as pd
from multiprocessing import Process, Queue
pd.options.mode.chained_assignment = None

dic_naming = {
    "name": "Название",
    "get_salary": "Оклад",
    "area_name": "Название региона",
    "published_at": "Дата публикации вакансии"
}


class UserInput:
    def __init__(self):
        # self.file_name = input('Введите название файла: ')
        # self.job_name = input('Введите название профессии: ')

        self.file_name = 'csv_files_dif_currencies'
        self.job_name = 'Аналитик'


def fill_df(df, currencies):
    currencies_to_work = list(currencies.loc[:, ~currencies.columns.isin(['date', 'Unnamed: 0'])].columns.values) + ['RUR']
    df = df[df['salary_currency'].isin(currencies_to_work)]
    df['salary'] = df.apply(lambda x: get_salary(x, currencies), axis=1)
    df.drop(columns=['salary_from', 'salary_to', 'salary_currency'], inplace=True)
    df = df.reindex(columns=['name', 'salary', 'area_name', 'published_at'], copy=True)
    return df


def get_salary(x, currencies):
    salary_from, salary_to, salary_currency, published_at = x.loc['salary_from'], x.loc['salary_to'], x.loc['salary_currency'], x.loc['published_at']
    date = published_at[:7]
    if math.isnan(salary_to) or math.isnan(salary_from):
        salary = salary_to if math.isnan(salary_from) else salary_from
    else:
        salary = math.floor((salary_from + salary_to) / 2)
    if salary_currency == 'RUR':
        return salary
    return math.floor(salary * currencies.loc[currencies['date'] == date][salary_currency].values[0])


def calc_year_stat_mp(file_name, job_name, q, currencies):
    df = pd.read_csv(file_name)
    df = fill_df(df, currencies)
    data_job = df[df['name'].str.contains(job_name, case=False)]

    q.put([int(df['published_at'].values[0][:4]), df.shape[0], math.floor(df['salary'].mean()), data_job.shape[0], math.floor(data_job['salary'].mean()), df])


def calc_year_stats_mp():
    global year_by_vac_num, year_by_salary, year_by_vac_num_job, year_by_salary_job, df_res
    process = []
    q = Queue()
    currencies = pd.read_csv('currencies.csv')
    for file_name in os.listdir(user_input.file_name):
        p = Process(target=calc_year_stat_mp, args=(user_input.file_name + '/' + file_name, user_input.job_name, q, currencies.copy()))
        process.append(p)
        p.start()

    for p in process:
        p.join(1)
        data = q.get()
        year_by_vac_num[data[0]] = data[1]
        year_by_salary[data[0]] = data[2]
        year_by_vac_num_job[data[0]] = data[3]
        year_by_salary_job[data[0]] = data[4]
        df_res.append(data[5])

    year_by_vac_num = dict(sorted(year_by_vac_num.items(), key=lambda i: i[0]))
    year_by_salary = dict(sorted(year_by_salary.items(), key=lambda i: i[0]))
    year_by_vac_num_job = dict(sorted(year_by_vac_num_job.items(), key=lambda i: i[0]))
    year_by_salary_job = dict(sorted(year_by_salary_job.items(), key=lambda i: i[0]))


def calc_area_stats():
    global vac_num_by_area, salary_by_area
    # currencies = pd.read_csv('currencies.csv')
    # df = pd.read_csv('csv_files_dif_currencies/part_2007.csv')
    # df = fill_df(df, currencies)
    df = pd.concat(df_res, ignore_index=True)
    # df.head(100).to_csv('3-2-2.csv', index=False, encoding='utf8')
    all_vac_num = df.shape[0]
    vac_percent = int(all_vac_num * 0.01)

    data = df.groupby('area_name')['name'] \
        .count() \
        .apply(lambda x: round(x / all_vac_num, 4)) \
        .sort_values(ascending=False) \
        .head(10) \
        .to_dict()
    vac_num_by_area = data

    area_vac_num = df.groupby('area_name')['name']\
        .count()\
        .loc[lambda x: x > vac_percent]\
        .to_dict()

    data = df.loc[df['area_name'].isin(area_vac_num.keys())]\
        .groupby('area_name')['salary']\
        .mean()\
        .apply(lambda x: math.floor(x))\
        .sort_values(ascending=False)\
        .head(10)\
        .to_dict()
    salary_by_area = data


def print_stats():
    print(f'Динамика уровня зарплат по годам: {year_by_salary}')
    print(f'Динамика количества вакансий по годам: {year_by_vac_num}')
    print(f'Динамика уровня зарплат по годам для выбранной профессии: {year_by_salary_job}')
    print(f'Динамика количества вакансий по годам для выбранной профессии: {year_by_vac_num_job}')
    print(f'Уровень зарплат по городам (в порядке убывания): {salary_by_area}')
    print(f'Доля вакансий по городам (в порядке убывания): {vac_num_by_area}')


if __name__ == '__main__':
    year_by_vac_num = {}
    year_by_salary = {}
    year_by_vac_num_job = {}
    year_by_salary_job = {}
    vac_num_by_area = {}
    salary_by_area = {}
    df_res = []

    user_input = UserInput()
    calc_year_stats_mp()
    calc_area_stats()
    print_stats()
