import math
import time
import pandas as pd
from multiprocessing import Process

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

        self.file_name = 'vacancies_by_year.csv'
        self.job_name = 'Аналитик'


class DataSet:
    def __init__(self):
        self.year_by_vac_num = {}
        self.year_by_salary = {}
        self.year_by_vac_num_job = {}
        self.year_by_salary_job = {}
        self.vac_num_by_area = {}
        self.salary_by_area = {}
        self.df = pd.read_csv(user_input.file_name)

        self.fill_df()
        self.all_vac_num = self.df.shape[0]

    def fill_df(self):
        self.df['year'] = self.df['published_at'].apply(lambda x: int(x[0:4]))
        self.df['currency_to_rub'] = self.df['salary_currency'].apply(lambda x: currency_to_rub[x])
        self.df['average_salary'] = self.df[['salary_from', 'salary_to']].mean(axis=1).apply(lambda x: math.floor(x))
        self.df['average_salary'] = self.df['average_salary'] * self.df['currency_to_rub']
        self.all_vac_num = self.df.shape[0]

    # Без многопроцессорной обработки
    # def calc_year_stats(self):
    #     for year in self.df['year'].unique():
    #         self.calc_year_stat(year)

    # С многопроцессорной обработкой
    def calc_year_stats(self):
        process = []
        for year in self.df['year'].unique():
            p = Process(target=self.calc_year_stat, args=(year, user_input.job_name))
            process.append(p)
            p.start()
            # self.calc_year_stat(year)
        for p in process:
            p.join()

    def calc_year_stat(self, year, job_name):
        data = self.df[self.df['year'] == year]
        self.year_by_vac_num[year] = data.shape[0]
        self.year_by_salary[year] = math.floor(data['average_salary'].mean())

        data_job = data[data['name'].str.contains(job_name, case=False)]
        self.year_by_vac_num_job[year] = data_job.shape[0]
        self.year_by_salary_job[year] = math.floor(data_job['average_salary'].mean())

    def calc_area_stats(self):
        vac_percent = int(self.all_vac_num * 0.01)

        data = self.df.groupby('area_name')['name'] \
            .count() \
            .apply(lambda x: round(x / self.all_vac_num, 4)) \
            .sort_values(ascending=False) \
            .head(10) \
            .to_dict()
        self.vac_num_by_area = data

        area_vac_num = self.df.groupby('area_name')['name']\
            .count()\
            .loc[lambda x: x > vac_percent]\
            .to_dict()

        data = self.df.loc[self.df['area_name'].isin(area_vac_num.keys())]\
            .groupby('area_name')['average_salary']\
            .mean()\
            .apply(lambda x: math.floor(x))\
            .sort_values(ascending=False)\
            .head(10)\
            .to_dict()
        self.salary_by_area = data

    def print(self):
        print(f'Динамика уровня зарплат по годам: {self.year_by_salary}')
        print(f'Динамика количества вакансий по годам: {self.year_by_vac_num}')
        print(f'Динамика уровня зарплат по годам для выбранной профессии: {self.year_by_salary_job}')
        print(f'Динамика количества вакансий по годам для выбранной профессии: {self.year_by_vac_num_job}')
        print(f'Уровень зарплат по городам (в порядке убывания): {self.salary_by_area}')
        print(f'Доля вакансий по городам (в порядке убывания): {self.vac_num_by_area}')


# def year_st(year):
#     data = df[df['year'] == year]
#     vac_num = data.shape[0]
#     average_salary = math.floor(data['average_salary'].mean())
#     return vac_num, average_salary
#
#
# def job_st(year, job_name):
#     data = df[df['year'] == year]
#     data_job = data[data['name'].str.contains(job_name, case=False)]
#     vac_num_job = data_job.shape[0]
#     av_s_job = math.floor(data_job['average_salary'].mean())
#     return vac_num_job, av_s_job

#
# def area_st_vac_num():
#     data = df.groupby('area_name')['name']\
#         .count()\
#         .apply(lambda x: round(x/all_vac_num, 4))\
#         .sort_values(ascending=False)\
#         .head(10)\
#         .to_dict()
#     return data
#
#
# def area_st_salary():
#     vac_percent = int(all_vac_num * 0.01)
#     area_vac_num = df.groupby('area_name')['name']\
#         .count()\
#         .loc[lambda x: x > vac_percent]\
#         .to_dict()
#
#     data = df.loc[df['area_name'].isin(area_vac_num.keys())]\
#         .groupby('area_name')['average_salary']\
#         .mean()\
#         .apply(lambda x: math.floor(x))\
#         .sort_values(ascending=False)\
#         .head(10)\
#         .to_dict()
#     return data



# file = 'vacancies_by_year.csv'
# df = pd.read_csv(file)
#
# df['year'] = df['published_at'].apply(lambda x: int(x[0:4]))
# df['currency_to_rub'] = df['salary_currency'].apply(lambda x: currency_to_rub[x])
# df['average_salary'] = df[['salary_from', 'salary_to']].mean(axis=1).apply(lambda x: math.floor(x))
# df['average_salary'] = df['average_salary'] * df['currency_to_rub']
# all_vac_num = df.shape[0]


# year_by_vac_num = {}
# year_by_salary = {}
# year_by_vac_num_job = {}
# year_by_salary_job = {}
# for year in df['year'].unique():
#     year_stats = year_st(year)
#     job_stats = job_st(year, user_input.job_name)
#     year_by_vac_num[year] = year_stats[0]
#     year_by_salary[year] = year_stats[1]
#     year_by_vac_num_job[year] = job_stats[0]
#     year_by_salary_job[year] = job_stats[1]
#
#
# vac_num_by_area = area_st_vac_num()
# salary_by_area = area_st_salary()
#
# print(year_by_vac_num)
# print(year_by_salary)
# print(year_by_vac_num_job)
# print(year_by_salary_job)
# print(vac_num_by_area)
# print(salary_by_area)


# def main():
#     user_input = UserInput()
#     data_set = DataSet()
#     data_set.print()

if __name__ == '__main__':
    start_time = time.time()
    user_input = UserInput()
    data_set = DataSet()
    data_set.calc_year_stats()
    data_set.calc_area_stats()
    data_set.print()
    print()
    # print("Время работы без многопроцессорной обработки: %s seconds" % round(time.time() - start_time, 4))
    print("Время работы c многопроцессорной обработкой: %s seconds" % round(time.time() - start_time, 4))
