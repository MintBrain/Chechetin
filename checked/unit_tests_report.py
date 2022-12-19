import unittest
from unittest import TestCase
from report_doc import Salary, Vacancy, Statistics, UserInput


class SalaryTests(TestCase):
    def test_salary_type(self):
        self.assertEqual(type(Salary('10.0', '20.4', 'RUR')).__name__, 'Salary')

    def test_salary_from(self):
        self.assertEqual(Salary('10.0', '20.4', 'RUR').salary_from, 10.0)

    def test_salary_to(self):
        self.assertEqual(Salary('10.0', '20.4', 'RUR').salary_to, 20.4)

    def test_salary_currency(self):
        self.assertEqual(Salary('10.0', '20.4', 'RUR').salary_currency, 'RUR')

    def test_average_salary_RUR(self):
        self.assertEqual(Salary('10.0', '20.4', 'RUR').average_salary, 15)

    def test_average_salary_USD(self):
        self.assertEqual(Salary('10.0', '20.4', 'USD').average_salary, 909.9)


class VacancyTests(TestCase):
    def test_vacancy_type(self):
        self.assertEqual(type(Vacancy(['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'], Statistics(), UserInput())).__name__, 'Vacancy')

    def test_vacancy_name(self):
        self.assertEqual(Vacancy(['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'], Statistics(), UserInput()).name, 'IT аналитик')

    def test_vacancy_area_name(self):
        self.assertEqual(Vacancy(['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'], Statistics(), UserInput()).area_name, 'Санкт-Петербург')

    def test_vacancy_published_at(self):
        self.assertEqual(Vacancy(['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'], Statistics(), UserInput()).published_at.timestamp(), 1196692476.0)

    def test_vacancy_clean_value_str(self):
        self.assertEqual(Vacancy.clean_value(['IT аналитик']), 'IT аналитик')

    def test_vacancy_clean_value_num(self):
        self.assertEqual(Vacancy.clean_value(['35000.0']), '35000.0')

    def test_vacancy_clean_value_date(self):
        self.assertEqual(Vacancy.clean_value(['2007-12-03T17:34:36+0300']), '2007-12-03T17:34:36+0300')

    def test_vacancy_clean_value_html_tag(self):
        self.assertEqual(Vacancy.clean_value(['<p> IT аналитик </p>']), 'IT аналитик')


if __name__ == '__main__':
    unittest.main()
