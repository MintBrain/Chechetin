import report
from checked import table

if __name__ == '__main__':
    if input('Введите данные для печати: ') == 'Статистика':
        report.main()
    else:
        table.main()
