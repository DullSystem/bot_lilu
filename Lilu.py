import openpyxl
import datetime

wb = openpyxl.reader.excel.load_workbook(filename='Lilu.xlsx')

wb.active = 0
sheet = wb.active
# print(sheet['A2'].value)

# на это листе мы привязываем дату и время к человеку

date = input('Какое число вы хотите? ')
def for_recording(date):
    try :
        for i in range(1,33):
            a = sheet['D' + str(i)].value, sheet['E' + str(i)].value, sheet['F' + str(i)].value
            if i == int(date):
                print(sheet['B' + str(i)].value, sheet['C' + str(i)].value, sheet['D' + str(i)].value, sheet['E' + str(i)].value,sheet['F' + str(i)].value)
                for y in a:
                    # перебор циклом, чтобы узнать сущетсвует ли запись на данный день
                    if y == '-':
                        print('К сожалению запись на данный день отсутствует, попробуйте выбрать другой день!')
                        exit()
                global time1
                time1 = input(str('Какое время вы хотите? '))
                if time1 == '09:00':
                    print(f'Забронировано! {date} число в {time1}')
                elif time1 == '11:30':
                    print(f'Забронировано! {date} число в {time1}')
                elif time1 == '14:30':
                    print(f'Забронировано! {date} число в {time1}')
                else:
                    print('Проверьте правильность запроса!')
                    try_again = input('Попробовать еще раз?[да/нет]')
                    while True:
                        if try_again.lower() == 'да':
                            for_recording(date)
                            break
                        else:
                            exit()
            elif int(date) >31:
                print('К сожалению столько дней в этом месяце нету ¯\_(ツ)_/¯ ')
                break
    except ValueError:
        print('Error_404')
        print('Я не понимаю о чем вы ¯\_(ツ)_/¯')
for_recording(date)
date1 = int(date)

time2 = time1