import gspread
import re
gc = gspread.service_account(filename='dullsystemm.json') #Делаем файл json и вставляем в папку с проектом, с гугл API
sh = gc.open('Lilu') #Открываем нужный нам файл в гугл таблицах

worksheet = sh.get_worksheet(0) # Лист первый, доступные даты на этот месяц
worksheet2 = sh.get_worksheet(2) # Лист третий, доступные даты на следующий месяц

worksheet_list=re.sub("[id0123456789Worksheet:><' ]","",str(worksheet))
worksheet_list2=re.sub("[id0123456789Worksheet:><' ]","",str(worksheet2))


# Здесь лежит имя листа = нужный нам месяц и мы присваеваем месяц к нужной цифры для счётчика таймера





def months_number():
    y = worksheet_list

    if y == 'Январь':
        return (1)
    elif y == 'Февраль':
        return (2)
    elif y == 'Март':
        return (3)
    elif y == 'Апрель':
        return (4)
    elif y == 'Май':
        return (5)
    elif y == 'Июнь':
        return (6)
    elif y == 'Июль':
        return (7)
    elif y == 'Август':
        return (8)
    elif y == 'Сентябрь':
        return (9)
    elif y == 'Октябрь':
        return (10)
    elif y == 'Ноябрь':
        return (11)
    elif y == 'Декабрь':
        return (12)

months_number()

def months_number1():
    y = worksheet_list2
    if y == 'Январь':
        return (1)
    elif y == 'Февраль':
        return (2)
    elif y == 'Март':
        return (3)
    elif y == 'Апрель':
        return (4)
    elif y == 'Май':
        return (5)
    elif y == 'Июнь':
        return (6)
    elif y == 'Июль':
        return (7)
    elif y == 'Август':
        return (8)
    elif y == 'Сентябрь':
        return (9)
    elif y == 'Октябрь':
        return (10)
    elif y == 'Ноябрь':
        return (11)
    elif y == 'Декабрь':
        return (12)

months_number1()
