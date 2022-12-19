import copy
import csv
import math
import re
import sys
import prettytable
from datetime import datetime
from prettytable import PrettyTable

dic_naming = {
    "name": "Название",
    "description": "Описание",
    "key_skills": "Навыки",
    "experience_id": "Опыт работы",
    "premium": "Премиум-вакансия",
    "employer_name": "Компания",
    "salary": "Оклад",
    "area_name": "Название региона",
    "published_at": "Дата публикации вакансии"
}
rus_experience_id = {
    "noExperience": "Нет опыта",
    "between1And3": "От 1 года до 3 лет",
    "between3And6": "От 3 до 6 лет",
    "moreThan6": "Более 6 лет",
}
rus_salary_currency = {
    "AZN": "Манаты",
    "BYR": "Белорусские рубли",
    "EUR": "Евро",
    "GEL": "Грузинский лари",
    "KGS": "Киргизский сом",
    "KZT": "Тенге",
    "RUR": "Рубли",
    "UAH": "Гривны",
    "USD": "Доллары",
    "UZS": "Узбекский сум",
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
        self.file_name = input('Введите название файла: ')
        self.filter_param = input('Введите параметр фильтрации: ').split(': ')
        self.sort_param = input('Введите параметр сортировки: ')
        self.reverse_sort = input('Обратный порядок сортировки (Да / Нет): ')
        self.start_end = input('Введите диапазон вывода: ').split()
        self.fields = ['№'] + input('Введите требуемые столбцы: ').split(', ')

        # self.file_name = 'vacancies_medium2.csv'
        # self.filter_param = 'Опыт работы: От 3 до 6 лет'.split(': ')
        # self.sort_param = 'Оклад'
        # self.reverse_sort = 'Нет'
        # self.start_end = '1 20'.split()
        # self.fields = ['№', 'Название', 'Навыки', 'Опыт работы', 'Компания', 'Оклад']

        self.check_filter_param()
        self.check_sort_param()

    def check_filter_param(self):
        if len(self.filter_param) == 1 and self.filter_param[0] == '':
            self.filter_param = 'Нет параметров'
        elif len(self.filter_param) == 1 and self.filter_param[0] != '':
            print('Формат ввода некорректен')
            sys.exit()
        elif self.filter_param[0] not in list(dic_naming.values()) + ['Идентификатор валюты оклада']:
            print('Параметр поиска некорректен')
            sys.exit()

    def check_sort_param(self):
        if self.sort_param == '':
            self.sort_param = 'Не сортировать'
        elif self.sort_param not in dic_naming.values():
            print('Параметр сортировки некорректен')
            sys.exit()
        elif self.reverse_sort not in ['Да', 'Нет', '']:
            print('Порядок сортировки задан некорректно')
            sys.exit()
        if self.reverse_sort == '':
            self.reverse_sort = False
        else:
            self.reverse_sort = bool_convert(self.reverse_sort)

    def check_cut_params(self, counter):
        if len(self.start_end) == 0:
            self.start_end.extend([0, counter])
        elif len(self.start_end) == 1:
            self.start_end[0] = int(self.start_end[0]) - 1
            self.start_end.append(counter)
        else:
            self.start_end = [int(item) - 1 for item in self.start_end]
        if self.fields[1] == '':
            self.fields = ['№'] + list(dic_naming.values())


class DataSet:
    def __init__(self, user_input):
        self.file_name = user_input.file_name
        self.csv_headers, self.readed_data = self.csv_reader()
        self.vacancies_objects = []
        self.csv_filter()

    def csv_reader(self):
        vacancies_file = open(self.file_name, encoding='utf_8_sig')
        vacancies_reader = csv.reader(vacancies_file)
        file_len = len(vacancies_file.readlines())
        if file_len == 0:
            print("Пустой файл")
            sys.exit()
        elif file_len == 1:
            print("Нет данных")
            sys.exit()
        vacancies_file.seek(0)
        return [vacancies_reader.__next__(), [x for x in vacancies_reader]]

    def csv_filter(self):
        for vacancy_data in self.readed_data:
            if len(vacancy_data) == len(self.csv_headers) and vacancy_data.count('') == 0:
                self.vacancies_objects.append(Vacancy(vacancy_data))

    def print_table(self, user_input):
        counter = 0
        table = PrettyTable(['№'] + list(dic_naming.values()), align='l', hrules=prettytable.ALL, max_width=20)
        print_data = []

        for vacancy in self.vacancies_objects:
            formatted_vacancy = copy.deepcopy(vacancy)
            formatted_data = formatted_vacancy.formatter()
            if formatted_data.vacancy_filter(user_input.filter_param, vacancy):
                counter += 1
                print_data.append([counter] + list(formatted_data.values()) + [vacancy])
        self.sort_data(print_data, table, user_input)
        if counter == 0:
            print('Ничего не найдено')
            sys.exit()
        user_input.check_cut_params(counter)
        print(table.get_string(start=user_input.start_end[0], end=user_input.start_end[1], fields=user_input.fields))

    @staticmethod
    def sort_data(print_data, table, user_input):
        sort_param = user_input.sort_param
        reverse_sort = user_input.reverse_sort
        if sort_param == 'Не сортировать':
            table.add_rows([x[:-1] for x in print_data])
            return
        if sort_param in ['Название', 'Описание', 'Премиум-вакансия', 'Компания', 'Название региона']:
            print_data = sorted(print_data,
                                key=lambda l: str(l[list(dic_naming.values()).index(sort_param) + 1]),
                                reverse=reverse_sort)
        elif sort_param == 'Оклад':
            print_data = sorted(print_data,
                                key=lambda l: l[-1].salary.average_salary * currency_to_rub[
                                    l[-1].salary.salary_currency],
                                reverse=reverse_sort)
        elif sort_param == 'Навыки':
            print_data = sorted(print_data, key=lambda l: l[-1].skills_count, reverse=reverse_sort)
        elif sort_param == 'Дата публикации вакансии':
            print_data = sorted(print_data, key=lambda l: l[-1].published_at, reverse=reverse_sort)
        elif sort_param == 'Опыт работы':
            print_data = sorted(print_data, key=lambda l: list(rus_experience_id.values()).index(l[4]))

        for i in range(1, len(print_data) + 1):
            print_data[i - 1][0] = i
        table.add_rows([x[:-1] for x in print_data])


class Vacancy:
    def __init__(self, vacancy_data):
        vacancy_data = [self.clean_value(s.split('\n')) for s in vacancy_data]
        self.name = vacancy_data[0]
        self.description = vacancy_data[1]
        self.key_skills = vacancy_data[2]
        self.skills_count = len(self.key_skills) if type(self.key_skills) == list else 1
        self.experience_id = vacancy_data[3]
        self.premium = vacancy_data[4]
        self.employer_name = vacancy_data[5]
        self.salary = Salary(vacancy_data[6],
                             vacancy_data[7],
                             vacancy_data[8],
                             vacancy_data[9])
        self.area_name = vacancy_data[10]
        self.published_at = datetime.strptime(vacancy_data[11], "%Y-%m-%dT%H:%M:%S%z")

    @staticmethod
    def clean_value(strings):
        html_tag_pattern = re.compile('<.*?>')
        result = []
        for string in strings:
            string = re.sub(html_tag_pattern, '', string)
            string = ' '.join(string.split())
            string = string.strip()
            result.append(string)
        if len(result) == 1:
            return result[0]
        return result

    def formatter(self):
        format_number = lambda val: re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1 ", "%d" % float(val))

        self.key_skills = "\n".join(self.key_skills) if type(self.key_skills) == list else self.key_skills
        self.premium = bool_convert(self.premium)
        self.salary.salary_gross = 'Без вычета налогов' if self.salary.salary_gross == 'True' else 'С вычетом налогов'
        self.experience_id = rus_experience_id[self.experience_id]
        self.salary.salary_currency = rus_salary_currency[self.salary.salary_currency]
        self.published_at = self.published_at.strftime('%d.%m.%Y')
        self.salary = f'{format_number(self.salary.salary_from)} - ' + \
                      f'{format_number(self.salary.salary_to)} ' + \
                      f'({self.salary.salary_currency}) ' + \
                      f'({self.salary.salary_gross})'

        for key in dic_naming.keys():
            attr_val = str(self.__getattribute__(key))
            if len(attr_val) > 100:
                self.__setattr__(key, attr_val[:100] + '...')
        return self

    def vacancy_filter(self, filter_param, vacancy):
        if filter_param == 'Нет параметров':
            return True
        filter_key, filter_val = filter_param
        if filter_key in ['Название', 'Компания', 'Премиум-вакансия', 'Название региона', 'Опыт работы',
                          'Дата публикации вакансии']:
            return filter_val == self.__getattribute__(
                list(dic_naming.keys())[list(dic_naming.values()).index(filter_key)])
        elif filter_key == 'Описание':
            return filter_val == vacancy.description
        elif filter_key == 'Идентификатор валюты оклада':
            return filter_val == rus_salary_currency[vacancy.salary.salary_currency]
        elif filter_key == 'Оклад':
            return int(vacancy.salary.salary_from) <= int(filter_val) <= int(vacancy.salary.salary_to)
        elif filter_key == 'Навыки':
            filter_skills = filter_val.split(', ')
            return all(lookfor in iter(vacancy.key_skills) for lookfor in iter(filter_skills))
        return True

    def values(self):
        return [
            self.name,
            self.description,
            self.key_skills,
            self.experience_id,
            self.premium,
            self.employer_name,
            self.salary,
            self.area_name,
            self.published_at
        ]


class Salary:
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.salary_from = float(salary_from)
        self.salary_to = float(salary_to)
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency
        self.average_salary = math.floor((self.salary_from + self.salary_to) / 2)


def bool_convert(data):
    if data == 'True':
        return 'Да'
    elif data == 'False':
        return 'Нет'
    return data == 'Да'


def main():
    user_input = UserInput()
    data_set = DataSet(user_input)
    data_set.print_table(user_input)
