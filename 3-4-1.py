import math
import os
import shutil
import pandas as pd
import separate
import new_report
from multiprocessing import Process, Queue
pd.options.mode.chained_assignment = None


class Statistics:
    def __init__(self):
        self.year_by_vac_num = {}
        self.year_by_salary = {}
        self.year_by_vac_num_job = {}
        self.year_by_salary_job = {}
        self.vac_num_by_area = {}
        self.salary_by_area = {}

        # self.year_by_vac_num = {2003: 1070, 2004: 4322, 2005: 9364, 2006: 23057, 2007: 35341, 2008: 46657, 2009: 31081, 2010: 51686, 2011: 77413, 2012: 95137, 2013: 129438, 2014: 141439, 2015: 147608, 2016: 177251, 2017: 203556, 2018: 282917, 2019: 265999, 2020: 234858, 2021: 136553, 2022: 47293}
        # self.year_by_salary = {2003: 41304, 2004: 42967, 2005: 375738, 2006: 41317, 2007: 44449, 2008: 48411, 2009: 44811, 2010: 44657, 2011: 46448, 2012: 47967, 2013: 53548, 2014: 49078, 2015: 51739, 2016: 60931, 2017: 59541, 2018: 64914, 2019: 69847, 2020: 72264, 2021: 82594, 2022: 94704}
        # self.year_by_vac_num_job = {2003: 46, 2004: 181, 2005: 424, 2006: 869, 2007: 1367, 2008: 1628, 2009: 818, 2010: 1519, 2011: 2223, 2012: 2281, 2013: 2542, 2014: 3082, 2015: 3042, 2016: 4286, 2017: 5490, 2018: 6984, 2019: 7979, 2020: 7581, 2021: 4613, 2022: 1885}
        # self.year_by_salary_job = {2003: 38353, 2004: 41907, 2005: 44621, 2006: 43250, 2007: 53936, 2008: 56297, 2009: 53320, 2010: 52702, 2011: 60252, 2012: 63380, 2013: 62928, 2014: 63348, 2015: 59868, 2016: 61864, 2017: 64567, 2018: 70152, 2019: 79580, 2020: 86362, 2021: 98609, 2022: 106732}
        # self.vac_num_by_area = {'Москва': 0.3053, 'Санкт-Петербург': 0.1079, 'Минск': 0.0265, 'Новосибирск': 0.0241, 'Нижний Новгород': 0.0216, 'Екатеринбург': 0.0207, 'Казань': 0.0205, 'Ростов-на-Дону': 0.0165, 'Алматы': 0.0165, 'Краснодар': 0.0158}
        # self.salary_by_area = {'Москва': 83695, 'Киев': 79891, 'Минск': 74149, 'Санкт-Петербург': 68747, 'Новосибирск': 64796, 'Екатеринбург': 59139, 'Краснодар': 51585, 'Казань': 51309, 'Нижний Новгород': 49915, 'Самара': 49548}


class UserInput:
    def __init__(self):
        # self.file_name = input('Введите название файла: ')
        # self.job_name = input('Введите название профессии: ')

        self.file_name = 'vacancies_dif_currencies.csv'
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
    global st, df_res
    process = []
    q = Queue()
    currencies = pd.read_csv('currencies.csv')
    for file_name in os.listdir(temp_folder):
        p = Process(target=calc_year_stat_mp, args=(temp_folder + '/' + file_name, user_input.job_name, q, currencies.copy()))
        process.append(p)
        p.start()

    for p in process:
        p.join(1)
        data = q.get()
        st.year_by_vac_num[data[0]] = data[1]
        st.year_by_salary[data[0]] = data[2]
        st.year_by_vac_num_job[data[0]] = data[3]
        st.year_by_salary_job[data[0]] = data[4]
        df_res.append(data[5])

    st.year_by_vac_num = dict(sorted(st.year_by_vac_num.items(), key=lambda i: i[0]))
    st.year_by_salary = dict(sorted(st.year_by_salary.items(), key=lambda i: i[0]))
    st.year_by_vac_num_job = dict(sorted(st.year_by_vac_num_job.items(), key=lambda i: i[0]))
    st.year_by_salary_job = dict(sorted(st.year_by_salary_job.items(), key=lambda i: i[0]))


def calc_area_stats():
    global st
    # currencies = pd.read_csv('currencies.csv')
    # df = pd.read_csv('csv_files_dif_currencies/part_2007.csv')
    # df = fill_df(df, currencies)
    # df.head(100).to_csv('3-4-1.csv', index=False, encoding='utf8')
    df = pd.concat(df_res, ignore_index=True)
    all_vac_num = df.shape[0]
    vac_percent = int(all_vac_num * 0.01)

    data = df.groupby('area_name')['name'] \
        .count() \
        .apply(lambda x: round(x / all_vac_num, 4)) \
        .sort_values(ascending=False) \
        .head(10) \
        .to_dict()
    st.vac_num_by_area = data

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
    st.salary_by_area = data


def print_stats():
    print(f'Динамика уровня зарплат по годам: {st.year_by_salary}')
    print(f'Динамика количества вакансий по годам: {st.year_by_vac_num}')
    print(f'Динамика уровня зарплат по годам для выбранной профессии: {st.year_by_salary_job}')
    print(f'Динамика количества вакансий по годам для выбранной профессии: {st.year_by_vac_num_job}')
    print(f'Уровень зарплат по городам (в порядке убывания): {st.salary_by_area}')
    print(f'Доля вакансий по городам (в порядке убывания): {st.vac_num_by_area}')


if __name__ == '__main__':
    st = Statistics()
    df_res = []
    temp_folder = 'csv_files_dif_currencies_temp'

    user_input = UserInput()
    separate.main(user_input.file_name, temp_folder)
    calc_year_stats_mp()
    calc_area_stats()

    new_report.main(user_input, st)
    print_stats()
    shutil.rmtree(rf'./{temp_folder}')
