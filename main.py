import report
import table

# Пример изменения строки 2.2.3 в develop
if __name__ == '__main__':
    if input('Введите данные для печати: ') == 'Статистика':
        report.main()
    else:
        table.main()
