import math
import os
import time
import pandas as pd
from multiprocessing import Process, Queue

dic_naming = {
    "name": "Название",
    "salary": "Оклад",
    "area_name": "Название региона",
    "published_at": "Дата публикации вакансии"
}
currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}


class UserInput:
    def __init__(self):
        # self.file_name = input('Введите название файла: ')
        # self.job_name = input('Введите название профессии: ')

        self.file_name = 'csv_files'
        self.job_name = 'Аналитик'


def fill_df(df):
    df['currency_to_rub'] = df['salary_currency'].apply(lambda x: currency_to_rub[x])
    df['average_salary'] = df[['salary_from', 'salary_to']].mean(axis=1).apply(lambda x: math.floor(x))
    df['average_salary'] = df['average_salary'] * df['currency_to_rub']


def calc_year_stat(file_name, job_name):
    df = pd.read_csv(file_name)
    fill_df(df)
    data_job = df[df['name'].str.contains(job_name, case=False)]

    return [int(df['published_at'].values[0][:4]), df.shape[0], math.floor(df['average_salary'].mean()), data_job.shape[0], math.floor(data_job['average_salary'].mean())]


def calc_year_stats():
    global year_by_vac_num, year_by_salary, year_by_vac_num_job, year_by_salary_job
    for file_name in os.listdir(user_input.file_name):
        data = calc_year_stat(user_input.file_name + '/' + file_name, user_input.job_name)
        year_by_vac_num[data[0]] = data[1]
        year_by_salary[data[0]] = data[2]
        year_by_vac_num_job[data[0]] = data[3]
        year_by_salary_job[data[0]] = data[4]


def calc_year_stat_mp(file_name, job_name, q):
    df = pd.read_csv(file_name)
    fill_df(df)
    data_job = df[df['name'].str.contains(job_name, case=False)]

    q.put([int(df['published_at'].values[0][:4]), df.shape[0], math.floor(df['average_salary'].mean()), data_job.shape[0], math.floor(data_job['average_salary'].mean())])


def calc_year_stats_mp():
    global year_by_vac_num, year_by_salary, year_by_vac_num_job, year_by_salary_job
    process = []
    q = Queue()
    for file_name in os.listdir(user_input.file_name):
        p = Process(target=calc_year_stat_mp, args=(user_input.file_name + '/' + file_name, user_input.job_name, q))
        process.append(p)
        p.start()

    for p in process:
        p.join()
        data = q.get()
        year_by_vac_num[data[0]] = data[1]
        year_by_salary[data[0]] = data[2]
        year_by_vac_num_job[data[0]] = data[3]
        year_by_salary_job[data[0]] = data[4]

    year_by_vac_num = dict(sorted(year_by_vac_num.items(), key=lambda i: i[0]))
    year_by_salary = dict(sorted(year_by_salary.items(), key=lambda i: i[0]))
    year_by_vac_num_job = dict(sorted(year_by_vac_num_job.items(), key=lambda i: i[0]))
    year_by_salary_job = dict(sorted(year_by_salary_job.items(), key=lambda i: i[0]))


def calc_area_stats():
    global vac_num_by_area, salary_by_area
    df = pd.read_csv('vacancies_by_year.csv')
    fill_df(df)
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
        .groupby('area_name')['average_salary']\
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
    start_time = time.time()

    user_input = UserInput()
    year_by_vac_num = {}
    year_by_salary = {}
    year_by_vac_num_job = {}
    year_by_salary_job = {}
    vac_num_by_area = {}
    salary_by_area = {}

    calc_area_stats()
    calc_year_stats()
    print_stats()

    print()
    print("Время работы без многопроцессорной обработки: %s seconds" % round(time.time() - start_time, 4))
    print()
    year_by_vac_num = {}
    year_by_salary = {}
    year_by_vac_num_job = {}
    year_by_salary_job = {}
    vac_num_by_area = {}
    salary_by_area = {}
    start_time = time.time()
    calc_area_stats()
    calc_year_stats_mp()
    print_stats()

    print()
    print("Время работы c многопроцессорной обработкой: %s seconds" % round(time.time() - start_time, 4))
