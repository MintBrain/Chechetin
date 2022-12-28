import sqlite3
import pandas as pd


class Statistics:
    def __init__(self):
        self.year_by_vac_num = {}
        self.year_by_salary = {}
        self.year_by_vac_num_job = {}
        self.year_by_salary_job = {}
        self.vac_num_by_area = {}
        self.salary_by_area = {}


st = Statistics()
job_name = 'Аналитик'
conn = sqlite3.connect("vacancies_dif_currencies.sqlite")
cur = conn.cursor()

st.year_by_salary = pd.read_sql("SELECT SUBSTR(published_at, 1, 4) as ""Год"", ROUND(AVG(salary)) as 'Средняя з\п' "
                            "From vacancies_dif_currencies "
                            "GROUP BY SUBSTR(published_at, 1, 4)", conn)

st.year_by_vac_num = pd.read_sql("""SELECT SUBSTR(published_at, 1, 4) as 'Year', COUNT(*) as 'Vac_count' 
                            from vacancies_dif_currencies 
                            group by SUBSTR(published_at, 1, 4) """, conn)

st.year_by_salary_job = pd.read_sql(f"""SELECT SUBSTR(published_at, 1, 4) as 'Год',
                                                    ROUND(AVG(salary), 2) as 'Средняя з\п {job_name}'
                                                    from vacancies_dif_currencies 
                                                    where lower(name) LIKE '%{job_name.lower()}%'
                                                    group by SUBSTR(published_at, 1, 4)""", conn)

st.year_by_vac_num_job = pd.read_sql(f"""SELECT SUBSTR(published_at, 1, 4) as 'Год',
                                                    COUNT(*) as 'Кол-во вакансий {job_name}'
                                                    from vacancies_dif_currencies 
                                                    where lower(name) LIKE '%{job_name.lower()}%'
                                                    group by SUBSTR(published_at, 1, 4)""", conn)

st.salary_by_area = pd.read_sql("""SELECT area_name as 'Город',  ROUND(AVG(salary), 2) as 'Средняя з\п'
                                         from vacancies_dif_currencies 
                                         group by area_name
                                         having COUNT(*) >= (SELECT COUNT(*) FROM vacancies_dif_currencies) / 100
                                         ORDER BY ROUND(AVG(salary), 2) DESC 
                                         LIMIT 10""", conn)

st.vac_num_by_area = pd.read_sql("""SELECT area_name as 'Город',
                                                100 * COUNT(*)/(select COUNT(*) from vacancies_dif_currencies)  as 'Доля(%)'
                                                from vacancies_dif_currencies
                                                group by area_name
                                                having COUNT(*) >= (SELECT COUNT(*) FROM vacancies_dif_currencies) / 100
                                                ORDER BY COUNT(*) DESC 
                                                LIMIT 10""", conn)

print(f'Динамика уровня зарплат по годам:\n{st.year_by_salary}\n')
print(f'Динамика количества вакансий по годам:\n{st.year_by_vac_num}\n')
print(f'Динамика уровня зарплат по годам для выбранной профессии:\n{st.year_by_salary_job}\n')
print(f'Динамика количества вакансий по годам для выбранной профессии:\n{st.year_by_vac_num_job}\n')
print(f'Уровень зарплат по городам (в порядке убывания):\n{st.salary_by_area}\n')
print(f'Доля вакансий по городам (в порядке убывания):\n{st.vac_num_by_area}')
