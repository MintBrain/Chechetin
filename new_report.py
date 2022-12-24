import csv
import math
import re
import sys
import os.path
import pdfkit
import numpy as np
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader, Template


class Report:
    def __init__(self, user_input):
        self.heads_by_year = ['Год', 'Средняя зарплата', f'Средняя зарплата - {user_input.job_name}',
                              'Количество вакансий', f'Количество вакансий - {user_input.job_name}']
        self.heads_by_area = ['Город', 'Уровень зарплат', ' ', 'Город', 'Доля вакансий']

    def generate_pdf(self, st, user_input):
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
        for year, value in st.year_by_salary.items():
            rows_1.append([year, value, st.year_by_salary_job[year],
                           st.year_by_vac_num[year], st.year_by_vac_num_job[year]])
        table1 = tm.render(heads=self.heads_by_year, rows=rows_1)

        rows_2 = []
        for i in range(len(st.salary_by_area)):
            rows_2.append([list(st.salary_by_area.keys())[i], list(st.salary_by_area.values())[i], ' ',
                           list(st.vac_num_by_area.keys())[i], f'{round(list(st.vac_num_by_area.values())[i]*100, 2)}%'])
        table2 = tm.render(heads=self.heads_by_area, rows=rows_2)

        env = Environment(loader=FileSystemLoader('..'))
        template = env.get_template("pdf_template.html")
        pdf_template = template.render({'job_name': user_input.job_name, 'img_path': img_path, 'table1': table1, 'table2': table2})
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report_3-4-2.pdf', configuration=config, options={"enable-local-file-access": ""})

    def generate_image(self, st, user_input):
        fig = plt.figure()
        width = 0.4
        x_n = np.arange(len(st.year_by_salary.keys()))
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
        graf_1 = fig.add_subplot(221)
        graf_1.set_title('Уровень зарплат по городам')
        graf_1.bar(x_list1, st.year_by_salary.values(), width, label='средняя з/п')
        graf_1.bar(x_list2, st.year_by_salary_job.values(), width, label=f'з/п {user_input.job_name}')
        graf_1.set_xticks(x_n, st.year_by_salary.keys(), rotation='vertical')
        graf_1.tick_params(axis="both", labelsize=8)
        graf_1.legend(fontsize=8, loc='upper left')
        graf_1.grid(True, axis='y')

    @staticmethod
    def ax_2(st, user_input, fig, x_list1, x_list2, x_n, width):
        graf_2 = fig.add_subplot(222)
        graf_2.set_title('Количество вакансий по годам')
        graf_2.bar(x_list1, st.year_by_vac_num.values(), width, label='Количество вакансий')
        graf_2.bar(x_list2, st.year_by_vac_num_job.values(), width, label=f'Количество вакансий\n{user_input.job_name.lower()}')
        graf_2.set_xticks(x_n, st.year_by_salary.keys(), rotation='vertical')
        graf_2.tick_params(axis="both", labelsize=8)
        graf_2.legend(fontsize=8, loc='upper left')
        graf_2.grid(True, axis='y')

    @staticmethod
    def ax_3(st, fig):
        graf_3 = fig.add_subplot(223)
        graf_3.set_title('Уровень зарплат по городам')
        x_n = np.arange(len(st.salary_by_area.keys()))
        graf_3.barh(x_n, st.salary_by_area.values())
        graf_3.set_yticks(x_n, [key.replace(' ', '\n').replace('-', '-\n') for key in st.salary_by_area.keys()])
        graf_3.tick_params(axis='y', labelsize=6)
        graf_3.tick_params(axis="x", labelsize=8)
        graf_3.grid(True, axis='x')
        graf_3.invert_yaxis()

    @staticmethod
    def ax_4(st, fig):
        graf_4 = fig.add_subplot(224)
        graf_4.set_title('Доля вакансий по городам')
        data = [1 - sum(st.vac_num_by_area.values())] + list(st.vac_num_by_area.values())
        graf_4.pie(data, labels=['Другие'] + list(st.vac_num_by_area.keys()), textprops={'fontsize': 6})
        graf_4.axis('equal')


def main(user_input, st):
    rep = Report(user_input)
    rep.generate_pdf(st, user_input)
