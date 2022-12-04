import csv
import math
import re
import sys
import os.path
import pdfkit
import doctest
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template

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
    """
    Класс для представления введенных данных.

    Attributes:
        file_name (str): Название файла
        job_name (str): Название профессии
    """
    def __init__(self):
        """
        Инициализирует объект UserInput. Выполняет чтение из поля ввода.
        """
        # self.file_name = input('Введите название файла: ')
        # self.job_name = input('Введите название профессии: ')

        self.file_name = 'vacancies_by_year.csv'
        self.job_name = 'Аналитик'


class DataSet:
    """
    Класс для представления данных выборки.

    Attributes:
        file_name (str): Название файла
        csv_headers ([str]): Массив заголовков
        read_data ([str]): Массив строк с данными
        vacancies_objects ([Vacancy]): Массив обработанных данных класса Vacancy
    """
    def __init__(self, st, user_input):
        """
        Инициализирует объект DataSet. Вызывает методы для первичной обработки данных.

        Args:
            st (Statistics): Объект класса Statistics. Представляет данные по статистике.
            user_input (UserInput): Объект класса UserInput. Представляет данные о введенных данных
        """
        self.file_name = user_input.file_name
        self.csv_headers, self.read_data = self.csv_reader()
        self.vacancies_objects = []
        self.csv_filter(st, user_input)

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

    def csv_filter(self, st, user_input):
        """
        Обрабатывает строки данных переводя их в класс Vacancy
        """
        for vacancy_data in self.read_data:
            if len(vacancy_data) == len(self.csv_headers) and vacancy_data.count('') == 0:
                self.vacancies_objects.append(Vacancy(vacancy_data, st, user_input))


class Vacancy:
    """
    Класс для представления вакансии.

    Attributes:
        name (str): Название вакансии
        salary (Salary): Объект класса Salary представляющий зарплату.
        area_name (str): Название региона.
        published_at (datetime): Дата публикации.
    """
    def __init__(self, vacancy_data, st, user_input):
        """
        Инициализирует объект Vacancy. Заполняет поля вакансии. Добавляет данные вакансии в статистику.

        Args:
            vacancy_data ([str]): Массив строк с полями данных вакансии.
            st (Statistics): Объект класса Statistics. Представляет данные по статистике.
            user_input (UserInput): Объект класса UserInput. Представляет данные о введенных данных

            >>> type(Vacancy(['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'], Statistics(), UserInput())).__name__
            'Vacancy'
            >>> Vacancy(['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'], Statistics(), UserInput()).name
            'IT аналитик'
            >>> Vacancy(['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'], Statistics(), UserInput()).area_name
            'Санкт-Петербург'
            >>> Vacancy(['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'], Statistics(), UserInput()).published_at.timestamp()
            1196692476.0
        """
        vacancy_data = [self.clean_value(s.split('\n')) for s in vacancy_data]
        i, c = 0, 0
        if len(vacancy_data) > 6:
            i, c = 5, 6
        self.name = vacancy_data[0]
        self.salary = Salary(vacancy_data[i + 1],
                             vacancy_data[i + 2],
                             vacancy_data[c + 3])
        self.area_name = vacancy_data[c + 4]
        self.published_at = datetime.strptime(vacancy_data[c + 5], "%Y-%m-%dT%H:%M:%S%z")

        st.add_data(self, user_input)

    @staticmethod
    def clean_value(strings):
        """
        Очищает строки от html тегов, лишних пробелов.

        Args:
            strings (str or List[str]): Строка для очистки.

        Returns:
            str or List[str]: Очищенная строка

            >>> Vacancy.clean_value(['IT аналитик'])
            'IT аналитик'
            >>> Vacancy.clean_value(['35000.0'])
            '35000.0'
            >>> Vacancy.clean_value(['2007-12-03T17:34:36+0300'])
            '2007-12-03T17:34:36+0300'
            >>> Vacancy.clean_value(['<p> IT аналитик </p>'])
            'IT аналитик'
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


class Salary:
    """
    Класс для представления зарплаты.

    Attributes:
        salary_from (float): Нижняя граница вилки оклада
        salary_to (float): Верхняя граница вилки оклада
        salary_currency (str): Валюта оклада
        average_salary (int or float): Средняя зарплата в рублях
    """
    def __init__(self, salary_from, salary_to, salary_currency):
        """
        Инициализирует объект Salary. Конвертирует числа. Считает среднюю зарплату.

        Args:
            salary_from (str): Нижняя граница вилки оклада
            salary_to (str): Верхняя граница вилки оклада
            salary_currency (str): Валюта оклада

            >>> type(Salary('10.0', '20.4', 'RUR')).__name__
            'Salary'
            >>> Salary('10.0', '20.4', 'RUR').salary_from
            10.0
            >>> Salary('10.0', '20.4', 'RUR').salary_to
            20.4
            >>> Salary('10.0', '20.4', 'RUR').salary_currency
            'RUR'
            >>> Salary('10.0', '20.4', 'RUR').average_salary
            15
            >>> Salary('10.0', '20.4', 'USD').average_salary
            909.9
        """
        self.salary_from = float(salary_from)
        self.salary_to = float(salary_to)
        self.salary_currency = salary_currency
        self.average_salary = math.floor((self.salary_from + self.salary_to) / 2) * \
                              currency_to_rub[self.salary_currency]


class Statistics:
    """
    Класс для подсчета статистики.

    Attributes:
        year_to_salary (dict): Статистика зарплат по годам
        year_to_vac_num (dict): Статистика количества вакансий по годам
        year_to_salary_for_job (dict): Статистика зарплат по годам для выбранной профессии
        year_to_vac_num_for_job (dict): Статистика количества вакансий по годам для выбранной профессии
        area_to_salary (dict): Статистика зарплат по регионам
        area_to_vac_num (dict): Статистика количества вакансий по регионам
        sorted_area_salary (dict): Отсортированная статистика зарплат по регионам
        sorted_area_num (dict): Отсортированная статистика количества вакансий по регионам
    """
    def __init__(self):
        """
        Инициализирует объект Statistics.
        """
        self.year_to_salary = {}
        self.year_to_vac_num = {}
        self.year_to_salary_for_job = {}
        self.year_to_vac_num_for_job = {}
        self.area_to_salary = {}
        self.area_to_vac_num = {}
        self.sorted_area_salary = {}
        self.sorted_area_num = {}

    def add_data(self, vacancy, user_input):
        """
        Добавляет данные вакансии в статистику.

        Args:
            vacancy (Vacancy): Объект класса Vacancy. Представляет данные о вакансии
            user_input (UserInput): Объект класса UserInput. Представляет данные о введенных данных
        """
        self.year_to_salary[vacancy.published_at.year] = self.year_to_salary.setdefault(vacancy.published_at.year, 0) + vacancy.salary.average_salary
        self.year_to_vac_num[vacancy.published_at.year] = self.year_to_vac_num.setdefault(vacancy.published_at.year, 0) + 1
        self.area_to_salary[vacancy.area_name] = self.area_to_salary.setdefault(vacancy.area_name, 0) + vacancy.salary.average_salary
        self.area_to_vac_num[vacancy.area_name] = self.area_to_vac_num.setdefault(vacancy.area_name, 0) + 1
        if user_input.job_name.lower() in vacancy.name.lower():
            self.year_to_salary_for_job[vacancy.published_at.year] = self.year_to_salary_for_job.setdefault(vacancy.published_at.year, 0) + vacancy.salary.average_salary
            self.year_to_vac_num_for_job[vacancy.published_at.year] = self.year_to_vac_num_for_job.setdefault(vacancy.published_at.year, 0) + 1
        else:
            self.year_to_salary_for_job[vacancy.published_at.year] = self.year_to_salary_for_job.setdefault(vacancy.published_at.year, 0)
            self.year_to_vac_num_for_job[vacancy.published_at.year] = self.year_to_vac_num_for_job.setdefault(vacancy.published_at.year, 0)

    def calc_average(self, data_set):
        """
        Считает средние значения в целевых статистиках. Сортирует данные.

        Args:
            data_set (DataSet): Объект класса DataSet. Представляет данные для анализа.
        """
        self.year_to_salary = {k: self.average(k, v, self.year_to_vac_num) for k, v in self.year_to_salary.items()}
        self.area_to_salary = {k: self.average(k, v, self.area_to_vac_num) for k, v in self.area_to_salary.items()}
        self.year_to_salary_for_job = {k: self.average(k, v, self.year_to_vac_num_for_job) for k, v in self.year_to_salary_for_job.items()}

        area_salary_cut = {k: v for k, v in self.area_to_salary.items() if
                           self.area_to_vac_num[k] >= int(len(data_set.vacancies_objects) * 0.01)}
        self.sorted_area_salary = dict(sorted(area_salary_cut.items(), key=lambda i: i[1], reverse=True)[:10])

        area_num_cut = {k: round(v / len(data_set.vacancies_objects), 4) for k, v in self.area_to_vac_num.items() if
                        self.area_to_vac_num[k] >= int(len(data_set.vacancies_objects) * 0.01)}
        self.sorted_area_num = dict(sorted(area_num_cut.items(), key=lambda i: i[1], reverse=True)[:10])

    @staticmethod
    def average(year, num, dic):
        """
        Считает среднее значение в год.

        Args:
            year (int): Год для подсчета
            num (int): Сумма чисел
            dic (dict): Словарь с количеством чисел

        Returns:
            int: Среднее значение в год.
        """
        if year == 0 or num == 0:
            return 0
        return math.floor(num / dic[year])

    def print(self):
        """
        Печатает статистику в консоль.
        """
        print(f'Динамика уровня зарплат по годам: {self.year_to_salary}')
        print(f'Динамика количества вакансий по годам: {self.year_to_vac_num}')
        print(f'Динамика уровня зарплат по годам для выбранной профессии: {self.year_to_salary_for_job}')
        print(f'Динамика количества вакансий по годам для выбранной профессии: {self.year_to_vac_num_for_job}')
        print(f'Уровень зарплат по городам (в порядке убывания): {self.sorted_area_salary}')
        print(f'Доля вакансий по городам (в порядке убывания): {self.sorted_area_num}')


class Report:
    """
    Класс для подсчета статистики.

    Attributes:
        heads_by_year (list): Заголовки таблицы для статистики по годам.
        heads_by_area (list): Заголовки таблицы для статистики по регионам.
    """
    def __init__(self, user_input):
        """
        Инициализирует объект Report.

        Args:
            user_input (UserInput): Объект класса UserInput. Представляет данные о введенных данных
        """
        self.heads_by_year = ['Год', 'Средняя зарплата', f'Средняя зарплата - {user_input.job_name}',
                              'Количество вакансий', f'Количество вакансий - {user_input.job_name}']
        self.heads_by_area = ['Город', 'Уровень зарплат', ' ', 'Город', 'Доля вакансий']

    def generate_pdf(self, st, user_input):
        """
        Генерирует pdf-отчёт.

        Args:
            st (Statistics): Объект класса Statistics. Представляет данные по статистике.
            user_input (UserInput): Объект класса UserInput. Представляет данные о введенных данных
        """
        self.generate_image(st, user_input)
        img_path = os.path.abspath('graph_t.png')
        table_html_template = '''
        <table>
            <tr>
                {% for head in heads %}
                {% if head == ' ' %}
                <th class="empty">{{ head }}</th>
                {% else %}                    
                <th>{{ head }}</th>
                {% endif %}
                {% endfor %}
            </tr>
            <tbody>
                {% for row in rows %}
                <tr>
                {% for cell in row %}
                {% if cell == ' ' %}
                <td class="empty">{{cell}}</td>
                {% else %}
                <td>{{cell}}</td>
                {% endif %}
                {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
        '''
        tm = Template(table_html_template)
        rows_1 = []
        for year, value in st.year_to_salary.items():
            rows_1.append([year, value, st.year_to_salary_for_job[year],
                           st.year_to_vac_num[year], st.year_to_vac_num_for_job[year]])
        table1 = tm.render(heads=self.heads_by_year, rows=rows_1)

        rows_2 = []
        for i in range(len(st.sorted_area_salary)):
            rows_2.append([list(st.sorted_area_salary.keys())[i], list(st.sorted_area_salary.values())[i], ' ',
                           list(st.sorted_area_num.keys())[i], f'{round(list(st.sorted_area_num.values())[i]*100, 2)}%'])
        table2 = tm.render(heads=self.heads_by_area, rows=rows_2)

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("pdf_template.html")
        pdf_template = template.render({'job_name': user_input.job_name, 'img_path': img_path, 'table1': table1, 'table2': table2})
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options={"enable-local-file-access": ""})

    def generate_image(self, st, user_input):
        """
        Генерирует png-файл с графиками.

        Args:
            st (Statistics): Объект класса Statistics. Представляет данные по статистике.
            user_input (UserInput): Объект класса UserInput. Представляет данные о введенных данных.
        """
        fig = plt.figure()
        width = 0.4
        x_n = np.arange(len(st.year_to_salary.keys()))
        x_list1 = x_n - width / 2
        x_list2 = x_n + width / 2
        self.ax_1(st, user_input, fig, x_list1, x_list2, x_n, width)
        self.ax_2(st, user_input, fig, x_list1, x_list2, x_n, width)
        self.ax_3(st, fig)
        self.ax_4(st, fig)

        plt.tight_layout()
        plt.savefig('graph_t.png', dpi=300)

    @staticmethod
    def ax_1(st, user_input, fig, x_list1, x_list2, x_n, width):
        """
        Генерирует график № 1.

        Args:
            st (Statistics): Объект класса Statistics. Представляет данные по статистике.
            user_input (UserInput): Объект класса UserInput. Представляет данные о введенных данных.
            fig (figure): Поле для графиков.
            x_list1 (ndarray): Массив расстояний для отступа для столбцов № 1.
            x_list2 (ndarray): Массив расстояний для отступа для столбцов № 2.
            x_n (ndarray): Массив количества пунктов для подписи.
            width (int): Ширина столбца графика.
        """
        graf_1 = fig.add_subplot(221)
        graf_1.set_title('Уровень зарплат по городам')
        graf_1.bar(x_list1, st.year_to_salary.values(), width, label='средняя з/п')
        graf_1.bar(x_list2, st.year_to_salary_for_job.values(), width, label=f'з/п {user_input.job_name}')
        graf_1.set_xticks(x_n, st.year_to_salary.keys(), rotation='vertical')
        graf_1.tick_params(axis="both", labelsize=8)
        graf_1.legend(fontsize=8, loc='upper left')
        graf_1.grid(True, axis='y')

    @staticmethod
    def ax_2(st, user_input, fig, x_list1, x_list2, x_n, width):
        """
        Генерирует график № 2.

        Args:
            st (Statistics): Объект класса Statistics. Представляет данные по статистике.
            user_input (UserInput): Объект класса UserInput. Представляет данные о введенных данных.
            fig (figure): Поле для графиков.
            x_list1 (ndarray): Массив расстояний для отступа для столбцов № 1.
            x_list2 (ndarray): Массив расстояний для отступа для столбцов № 2.
            x_n (ndarray): Массив количества пунктов для подписи.
            width (int): Ширина столбца графика.
        """
        graf_2 = fig.add_subplot(222)
        graf_2.set_title('Количество вакансий по годам')
        graf_2.bar(x_list1, st.year_to_vac_num.values(), width, label='Количество вакансий')
        graf_2.bar(x_list2, st.year_to_vac_num_for_job.values(), width, label=f'Количество вакансий\n{user_input.job_name.lower()}')
        graf_2.set_xticks(x_n, st.year_to_salary.keys(), rotation='vertical')
        graf_2.tick_params(axis="both", labelsize=8)
        graf_2.legend(fontsize=8, loc='upper left')
        graf_2.grid(True, axis='y')

    @staticmethod
    def ax_3(st, fig):
        """
        Генерирует график № 3.

        Args:
            st (Statistics): Объект класса Statistics. Представляет данные по статистике.
            fig (figure): Поле для графиков.
        """
        graf_3 = fig.add_subplot(223)
        graf_3.set_title('Уровень зарплат по городам')
        x_n = np.arange(len(st.sorted_area_salary.keys()))
        graf_3.barh(x_n, st.sorted_area_salary.values())
        graf_3.set_yticks(x_n, [key.replace(' ', '\n').replace('-', '-\n') for key in st.sorted_area_salary.keys()])
        graf_3.tick_params(axis='y', labelsize=6)
        graf_3.tick_params(axis="x", labelsize=8)
        graf_3.grid(True, axis='x')
        graf_3.invert_yaxis()

    @staticmethod
    def ax_4(st, fig):
        """
        Генерирует график № 4.

        Args:
            st (Statistics): Объект класса Statistics. Представляет данные по статистике.
            fig (figure): Поле для графиков.
        """
        graf_4 = fig.add_subplot(224)
        graf_4.set_title('Доля вакансий по городам')
        data = [1 - sum(st.sorted_area_num.values())] + list(st.sorted_area_num.values())
        graf_4.pie(data, labels=['Другие'] + list(st.sorted_area_num.keys()), textprops={'fontsize': 6})
        graf_4.axis('equal')


def main():
    """
    Точка входа.
    """
    user_input = UserInput()
    st = Statistics()
    data_set = DataSet(st, user_input)
    st.calc_average(data_set)
    rep = Report(user_input)
    rep.generate_pdf(st, user_input)


if __name__ == '__main__':
    # main()
    doctest.testmod(report=True)
