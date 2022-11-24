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
    """
    Класс для представления введенных данных.

    Attributes:
        file_name (str): Название файла
        filter_param (list): Параметр фильтрации
        sort_param (str): Параметр сортировки
        reverse_sort (bool): Обратный порядок сортировки. По умолчанию False.
        start_end (list): Диапазон вывода данных таблицы.
        fields (list): Название столбцов для вывода.
    """
    def __init__(self):
        """
        Инициализирует объект UserInput. Выполняет чтение из поля ввода. Проверяет корректность.
        """
        self.file_name = input('Введите название файла: ')
        self.filter_param = input('Введите параметр фильтрации: ').split(': ')
        self.sort_param = input('Введите параметр сортировки: ')
        self.reverse_sort = input('Обратный порядок сортировки (Да / Нет): ')
        self.start_end = input('Введите диапазон вывода: ').split()
        self.fields = ['№'] + input('Введите требуемые столбцы: ').split(', ')

        self.check_filter_param()
        self.check_sort_param()

    def check_filter_param(self):
        """
        Проверяет параметр фильтрации на корректность.
        """
        if len(self.filter_param) == 1 and self.filter_param[0] == '':
            self.filter_param = 'Нет параметров'
        elif len(self.filter_param) == 1 and self.filter_param[0] != '':
            print('Формат ввода некорректен')
            sys.exit()
        elif self.filter_param[0] not in list(dic_naming.values()) + ['Идентификатор валюты оклада']:
            print('Параметр поиска некорректен')
            sys.exit()

    def check_sort_param(self):
        """
        Проверяет параметр сортировки на корректность.
        Преобразует переменную обратной сортировки в bool.
        """
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
        """
        Проверяет параметры диапазона и названия столбцов на корректность.

        Attributes:
            counter (int): Количество подходящих вакансий для вывода.
        """
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
    """
    Класс для представления данных выборки.

    Attributes:
        file_name (str): Название файла
        csv_headers ([str]): Массив заголовков
        read_data ([str]): Массив строк с данными
        vacancies_objects ([Vacancy]): Массив обработанных данных класса Vacancy
    """
    def __init__(self, user_input):
        """
        Инициализирует объект DataSet. Вызывает методы для первичной обработки данных.

        Args:
            user_input (UserInput): Объект класса UserInput. Представляет данные о введенных данных
        """
        self.file_name = user_input.file_name
        self.csv_headers, self.read_data = self.csv_reader()
        self.vacancies_objects = []
        self.csv_filter()

    def csv_reader(self):
        """
        Производит чтение данных из файла. Проверяет пустоту файла.

        Returns:
            List[Union[List[str], List[List[str]]]]: Список заголовков и список данных
        """
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
        """
        Обрабатывает строки данных переводя их в класс Vacancy
        """
        for vacancy_data in self.read_data:
            if len(vacancy_data) == len(self.csv_headers) and vacancy_data.count('') == 0:
                self.vacancies_objects.append(Vacancy(vacancy_data))

    def print_table(self, user_input):
        """
        Заполняет таблицу и выводит в консоль.
        """
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
        """
        Сортирует данные по параметру сортировки.

        Args:
            print_data (array): Массив вакансий.
            table (PrettyTable): Объект таблицы.
            user_input (UserInput): Объект класса UserInput. Представляет введенные данные.
        """
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
    """
    Класс для представления вакансии.

    Attributes:
        name (str): Название вакансии
        description (str): Описание вакансии
        key_skills (list or str): Навыки
        skills_count (int): Количество навыков
        experience_id (str): Опыт работы
        premium (str): Премиум-вакансия
        employer_name (str): Компания
        salary (Salary): Объект класса Salary представляющий зарплату.
        area_name (str): Название региона.
        published_at (datetime): Дата публикации.
    """
    def __init__(self, vacancy_data):
        """
        Инициализирует объект Vacancy. Заполняет поля вакансии.

        Args:
            vacancy_data ([str]): Массив строк с полями данных вакансии.
        """
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
        """
        Очищает строки от html тегов, лишних пробелов.

        Args:
            strings (str or List[str]): Строка для очистки.

        Returns:
            str or List[str]: Очищенная строка
        """
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
        """
        Русифицирует поля вакансии.

        Returns:
            Vacancy: Объект класса Vacancy. Представляет данные о вакансии
        """
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
        """
        Определяет подходит ли вакансия по параметру фильтрации.

        Args:
            filter_param (str or List[str]): Строка для очистки.
            vacancy (Vacancy): Объект класса Vacancy. Представляет данные о вакансии

        Returns:
            bool: Результат фильтра.
        """
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
        """
        Возвращает массив полей вакансии.

        Returns:
            list: Массив полей вакансии.
        """
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
    """
    Класс для представления зарплаты.

    Attributes:
        salary_from (float): Нижняя граница вилки оклада
        salary_to (float): Верхняя граница вилки оклада
        salary_gross (str): Оклад указан до вычета налогов
        salary_currency (str): Валюта оклада
        average_salary (int): Средняя зарплата.
    """
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        """
        Инициализирует объект Salary. Конвертирует числа. Считает среднюю зарплату.

        Args:
            salary_from (str): Нижняя граница вилки оклада
            salary_to (str): Верхняя граница вилки оклада
            salary_gross (str): Оклад указан до вычета налогов
            salary_currency (str): Валюта оклада
        """
        self.salary_from = float(salary_from)
        self.salary_to = float(salary_to)
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency
        self.average_salary = math.floor((self.salary_from + self.salary_to) / 2)


def bool_convert(data):
    """
    Преобразует bool в str и обратно.

    Args:
        data (str or bool): Объект для преобразования.

    Returns:
        str or bool: Преобразованный объект.
    """
    if data == 'True':
        return 'Да'
    elif data == 'False':
        return 'Нет'
    return data == 'Да'


def main():
    """
    Точка входа.
    """
    user_input = UserInput()
    data_set = DataSet(user_input)
    data_set.print_table(user_input)
