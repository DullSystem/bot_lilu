import telebot
from telebot import types
import datetime
import time
from keyboa import Keyboa
import Config
import gspread
import re


overwrite_user = {} #Словарь для передачи переменных из перезаписи
user_name = {} #Словарь имя, для сохранения
user_number = {} #Словарь номера для сохранения
user_date = {} #Словарь даты для сохранения
user_time1 = {} #Словарь время 1 для сохранения
user_time2 = {} #Словарь время 2 для сохранения
user_time3 = {} #Словарь время 3 для сохранения
user_worksheet_list = {}

gc = gspread.service_account(filename='dullsystemm.json') #Делаем файл json и вставляем в папку с проектом, с гугл API
sh = gc.open('Lilu') #Открываем нужный нам файл в гугл таблицах

worksheet = sh.get_worksheet(0) # Лист первый, доступные даты на этот месяц
worksheet1 = sh.get_worksheet(1) # На этот лист записывает и перезаписывает клиентов
worksheet2 = sh.get_worksheet(2) # Лист третий, доступные даты на следующий месяц

worksheet_list=re.sub("[id0123456789Worksheet:><' ]","",str(worksheet)) #Убираем лишние знаки, чтобы показать месяц определенным названием
worksheet_list2=re.sub("[id0123456789Worksheet:><' ]","",str(worksheet2))

bot = telebot.TeleBot(Config.TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Записаться') # Кнопка записаться
        item2 = types.KeyboardButton('Перезаписаться') # Кнопка перезаписаться
        item0 = types.KeyboardButton('Актуальный прайс')  # Кнопка перезаписаться
        item = types.KeyboardButton('Посмотреть забронированное время')  # Кнопка для поиска занятого времени в определённой дате
        markup.add(item1, item2,item0,item)

        bot.send_message(message.chat.id, 'Здравствуйте, {0.first_name}!\nЯ бот - <b>{1.first_name}</b>'.format(message.from_user, bot.get_me()),
        parse_mode= 'html',reply_markup= markup) # Бот здоровается



@bot.message_handler(content_types=['text'])

def message_lauch(message):
    # Бот предлагает 4 команды по кнопкам
    if message.text == 'Записаться':

        keyboard = types.InlineKeyboardMarkup()
        item3 = types.InlineKeyboardButton(text=f'{worksheet_list}', callback_data='first_sheet')
        keyboard.add(item3) # Записаться на месяц с первого листа Excel
        item4 = types.InlineKeyboardButton(text=f'{worksheet_list2}', callback_data='second_sheet')
        keyboard.add(item4) # Записаться на месяц со второго листа Excel

        bot.send_message(message.from_user.id, text='На какой месяц вы хотите записаться?', reply_markup=keyboard) # Тут подвязываем кнопки к тексту

    elif message.text == 'Перезаписаться':
        bot.send_message(message.from_user.id, str('Введите номер телефона без знака +: '))
        bot.register_next_step_handler(message, overwrite)

    elif message.text == 'Актуальный прайс':
        p=open('pryse.jpg','rb') #Картинка в каталоге с папкой

        bot.send_photo(message.from_user.id, photo=p)

    elif message.text == 'Посмотреть забронированное время':

        keyboard4 = types.InlineKeyboardMarkup()
        item10 = types.InlineKeyboardButton(text=f'{worksheet_list}', callback_data='first_month')
        keyboard4.add(item10)
        item11 = types.InlineKeyboardButton(text=f'{worksheet_list2}', callback_data='second_month')
        keyboard4.add(item11)
        bot.send_message(message.from_user.id, text='Какой месяц вы хотите посмотреть?', reply_markup=keyboard4)





def overwrite(message): # После кнопки перезаписаться открывается эта функция
    number1 = str(message.text)
    chat_id = message.chat.id # Наш id, чтобы привязывать его к словарю
    amount_re = re.compile(number1)
    cell_row = worksheet1.find(amount_re)  # Ищет наше значение в гугл таблицах
    if cell_row == None: #Значение не найдено
        bot.send_message(message.chat.id, 'К сожалению запись на данный номер отсутствует, попробуйте еще раз!')
    else:
        index_row = cell_row.row # Нужно передать для удаления строки
        overwrite_user[chat_id] = [index_row] #Добавляем номер строки и id в словарь

        # Получили номер строки, в которой находится значение
        line_number = int(worksheet1.cell(index_row,3).value) # Номер телефона
        line_name = str(worksheet1.cell(index_row,2).value) #Имя
        line_date = str(worksheet1.cell(index_row,4).value) #Дата
        line_month = str(worksheet1.cell(index_row,5).value) #Месяц
        line_time = str(worksheet1.cell(index_row,6).value) #Время

        bot.send_message(message.chat.id, f'Запись на имя: {line_name}')
        bot.send_message(message.chat.id, f'Номер телефона: {line_number}')
        bot.send_message(message.chat.id, f'На {line_date} число')
        bot.send_message(message.chat.id, f'Месяц {line_month}')
        bot.send_message(message.chat.id, f' Время: {line_time}')

        # Кнопки для для перезаписи
        keyboard1 = types.InlineKeyboardMarkup()
        item5 = types.InlineKeyboardButton(text='Да', callback_data='Yes')


        keyboard1.add(item5)

        item6 = types.InlineKeyboardButton(text='Нет', callback_data='No')
        keyboard1.add(item6)
        bot.send_message(message.from_user.id, text='Желаете перезаписаться? \nПредыдущая запись будет удалена', reply_markup=keyboard1,)




def full_name(message):
    name = message.text
    chat_id = message.chat.id
    user_name[chat_id] = [name] # Добавили имя в словарь
    bot.send_message(message.from_user.id, f'{name}, какой объём наращивания хотите сделать?')
    bot.register_next_step_handler(message, user_phone)



def user_phone(message):

    bot.send_message(message.from_user.id, 'Введите номер телефона без знака +: ')
    bot.register_next_step_handler(message, phone)




def phone(message):
    number = message.text
    chat_id = message.chat.id



    while True:
        while True:  # Номер должен состоять из 11 символов обязательно, делаем проверку
            if (number.isdigit()) == True: #Проверяем на наличие букв в номере
                break
            else:
                bot.send_message(message.from_user.id,'Пожалуйста введите номер только цифрами')
                break
        number1 = int(len(number))
        if number1 == 11:
            amount_re = re.compile(number)
            cell_row = worksheet1.find(amount_re) #Ищет наше значение в гугл таблицах
            if cell_row == None:
                user_number[chat_id] = [number]  # Добавили в словарь номер
                # Создаем клавиатуру для выбора даты
                numbers_date = list(range(1, 32))  #
                keyboard = Keyboa(items=numbers_date, items_in_row=7).keyboard
                bot.send_message(message.from_user.id, text='Пожалуйста выберете удобную для вас дату',reply_markup=keyboard)
                break
            else:
                bot.send_message(message.from_user.id, 'Запись на данный номер уже существует, попробуйте еще раз')
                user_phone(message)
                break
        elif number1 < 11:
            bot.send_message(message.from_user.id,'Слишком мало цифр')
            user_phone(message)
            break
        elif number1 > 11:
            bot.send_message(message.from_user.id,'Слишком много цифр')
            user_phone(message)
            break



def full_date(message, date_number):
    date = date_number #Значение пришло с клавиатуры
    day = datetime.date.today().day  # Переменная равна дате, которая в данный момент
    chat_id = message.chat.id
    user_date[chat_id] = [date] # Добавили дату в словарь
    month_sheet = ''.join(map(str, user_worksheet_list[chat_id])) # с помощью это переменной показываем либо первый месяц, либо второй
    try:
        if month_sheet == '0':
            if int(date) >= int(day):
                line_date = str(worksheet.cell(date, 1).value)  # Дата
                day_of_week = str(worksheet.cell(date, 2).value)  # День недели
                line_time1 = str(worksheet.cell(date, 3).value)  # Первое время на данную дату, добавляем в словарь
                user_time1[chat_id] = [line_time1]
                line_time2 = str(worksheet.cell(date, 4).value)  # Второе время на данную дату, добавляем в словарь
                user_time2[chat_id] = [line_time2]
                line_time3 = str(worksheet.cell(date, 5).value)  # Третье время на данную дату, добавляем в словарь
                user_time3[chat_id] = [line_time1]
                bot.send_message(message.chat.id, f'{worksheet_list} месяц')
                bot.send_message(message.chat.id, f'{line_date} число')
                bot.send_message(message.chat.id, day_of_week)

                # Время переводим сразу в кнопки, удобнее нажимать пользователю и не будет ошибок
                keyboard2 = types.InlineKeyboardMarkup()

                item5 = types.InlineKeyboardButton(text=f'{line_time1}',callback_data='time1')  # кнопка на первое время в эту дату
                keyboard2.add(item5)

                item6 = types.InlineKeyboardButton(text=f'{line_time2}', callback_data='time2')  # кнопка на второе время в эту дату
                keyboard2.add(item6)

                item7 = types.InlineKeyboardButton(text=f'{line_time3}', callback_data='time3')  # кнопка на третье время в эту дату
                keyboard2.add(item7)

                bot.send_message(message.chat.id, text='Какое время вас устроит?', reply_markup=keyboard2)

            elif int(date) < int(day):
                bot.send_message(message.chat.id, 'Кажется это число уже позади ¯\_(ツ)_/¯')
                welcome(message)
        elif month_sheet == '2': # Посмотреть даты на второй месяц
            line_date = str(worksheet2.cell(date, 1).value)  # Дата
            day_of_week = str(worksheet2.cell(date, 2).value)  # День недели
            line_time1 = str(worksheet2.cell(date, 3).value)  # Первое время на данную дату, добавляем в словарь
            user_time1[chat_id] = [line_time1]
            line_time2 = str(worksheet2.cell(date, 4).value)  # Второе время на данную дату, добавляем в словарь
            user_time2[chat_id] = [line_time2]
            line_time3 = str(worksheet2.cell(date, 5).value)  # Третье время на данную дату, добавляем в словарь
            user_time3[chat_id] = [line_time1]
            bot.send_message(message.chat.id, f'{worksheet_list2} месяц')
            bot.send_message(message.chat.id, f'{line_date} число')
            bot.send_message(message.chat.id, day_of_week)

            # Время переводим сразу в кнопки, удобнее нажимать пользователю и не будет ошибок
            keyboard2 = types.InlineKeyboardMarkup()

            item5 = types.InlineKeyboardButton(text=f'{line_time1}', callback_data='time1')  # кнопка на первое время в эту дату
            keyboard2.add(item5)

            item6 = types.InlineKeyboardButton(text=f'{line_time2}', callback_data='time2')  # кнопка на второе время в эту дату
            keyboard2.add(item6)

            item7 = types.InlineKeyboardButton(text=f'{line_time3}', callback_data='time3')  # кнопка на третье время в эту дату
            keyboard2.add(item7)

            bot.send_message(message.chat.id, text='Какое время вас устроит?', reply_markup=keyboard2)
    except ValueError:
        bot.send_message(message.from_user.id,'Error_404')
        bot.send_message(message.from_user.id,'Я не понимаю о чем вы ¯\_(ツ)_/¯')





def recording(message,timer):
    chat_id = message.chat.id
    day = datetime.date.today().day
    date = ''.join(map(str, user_date[chat_id]))
    month_sheet = ''.join(map(str, user_worksheet_list[chat_id]))  # с помощью это переменной показываем либо первый месяц, либо второй

    try:
        year = datetime.datetime.today().year # Год
        a = year # Месяц
        b = None # Пустая переменная
        import months # Число

        if month_sheet == '0':
            b = months.months_number() #Название листа будет соответствовать определенному значению
        elif month_sheet == '2':
            b = months.months_number1()

        c = message.text # пользователь выбрал через сколько дней ему напомнить

        today = datetime.date.today()

        date3 = datetime.date(a, b, int(c))
        delta = str(date3 - today)

        term = int(delta[0] + delta[1])

        #это колличество минут в сутках 1440 + еще 12 часов, напоминание в полдень за день до 2160
        local_time = term * 86400
        if month_sheet == '0': #Нельзя забронировать в этом месяце число, которое уже было
            if int(c) > int(day):
                if term == 1 or term == 21 or term == 31:
                    bot.send_message(message.chat.id, f'Напомню вам о записи через {term} день')

                elif term <= 4 or term == 24:
                    bot.send_message(message.chat.id, f'Напомню вам о записи через {term} дня')
                else:
                    bot.send_message(message.chat.id, f'Напомню вам о записи через {term} дней')

                time.sleep(local_time) #Переходит в сон, умножая колличество введенных дней на минуты в сутках

                bot.send_message(message.chat.id,
                                 f'Добрый день! \nНапоминаю, вы записаны на наращивание ресниц \n{date} числа, время: {timer}')
            else:
                bot.send_message(message.chat.id,'Увы, но надо жить настоящим, а не прошлым ¯\_(ツ)_/¯')
        if month_sheet == '2':
            if term == 1 or term == 21 or term == 31:
                bot.send_message(message.chat.id, f'Напомню вам о записи через {term} день')

            elif term <= 4 or term == 24:
                bot.send_message(message.chat.id, f'Напомню вам о записи через {term} дня')
            else:
                bot.send_message(message.chat.id, f'Напомню вам о записи через {term} дней')

            time.sleep(local_time) #Переходит в сон, умножая колличество введенных дней на минуты в сутках

            bot.send_message(message.chat.id,
                             f'Добрый день! \nНапоминаю, вы записаны на наращивание ресниц \n{date} числа, время: {timer}')

    except ValueError:
        bot.send_message(message.chat.id,'К сожалению вы не можете забронировать на данное число! ')
        exit()




def Busy_dates(message): #Проверить записи на число/первый лист
    busy_date = message.text
    try:
        if int(busy_date) <= 31:
            bot.send_message(message.chat.id, 'Придётся немного подождать, пока я все проверю :)')
            def Busy_recording():
                recording_user = int((worksheet1.cell(1, 1).value))
                recording_user1 = recording_user + 1
                if recording_user == None:
                    recording_user = 0
                else:
                    date_for_recording = f'{busy_date}{worksheet_list}'
                    index_line = 2
                    cell_date = worksheet1.cell(index_line, 4).value
                    cell_month = str(worksheet1.cell(index_line, 5).value)
                    cell_time = str(worksheet1.cell(index_line, 6).value)
                    cell_recording = str(f'{cell_date}{cell_month}')

                    if str(date_for_recording) == str(cell_recording):
                        bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                        while True:
                            if index_line <= recording_user1:  # Нельзя проходить больше строк, чем записанное колличество людей
                                while True:
                                    index_line += 1
                                    cell_date = worksheet1.cell(index_line, 4).value
                                    cell_month = str(worksheet1.cell(index_line, 5).value)
                                    cell_time = str(worksheet1.cell(index_line, 6).value)
                                    cell_recording = str(f'{cell_date}{cell_month}')
                                    if str(date_for_recording) == str(cell_recording):
                                        bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                        while True:
                                            index_line += 1
                                            cell_date = worksheet1.cell(index_line, 4).value
                                            cell_month = str(worksheet1.cell(index_line, 5).value)
                                            cell_time = str(worksheet1.cell(index_line, 6).value)
                                            cell_recording = str(f'{cell_date}{cell_month}')
                                            if str(date_for_recording) == str(cell_recording):
                                                bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                                while True:
                                                    index_line += 1
                                                    cell_date = worksheet1.cell(index_line, 4).value
                                                    cell_month = str(worksheet1.cell(index_line, 5).value)
                                                    cell_time = str(worksheet1.cell(index_line, 6).value)
                                                    cell_recording = str(f'{cell_date}{cell_month}')
                                                    if str(date_for_recording) == str(cell_recording):
                                                        return bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                                    else:
                                                        break
                                            else:
                                                break
                                    else:
                                        break
                            else:
                                break
                    elif str(date_for_recording) != str(cell_recording):
                        while True:
                            if index_line <= recording_user1:  # Нельзя проходить больше строк, чем записанное колличество людей
                                while True:
                                    index_line += 1
                                    cell_date = worksheet1.cell(index_line, 4).value
                                    cell_month = str(worksheet1.cell(index_line, 5).value)
                                    cell_time = str(worksheet1.cell(index_line, 6).value)
                                    cell_recording = str(f'{cell_date}{cell_month}')
                                    if str(date_for_recording) == str(cell_recording):
                                        bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                        while True:
                                            index_line += 1
                                            cell_date = worksheet1.cell(index_line, 4).value
                                            cell_month = str(worksheet1.cell(index_line, 5).value)
                                            cell_time = str(worksheet1.cell(index_line, 6).value)
                                            cell_recording = str(f'{cell_date}{cell_month}')
                                            if str(date_for_recording) == str(cell_recording):
                                                bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                                while True:
                                                    index_line += 1
                                                    cell_date = worksheet1.cell(index_line, 4).value
                                                    cell_month = str(worksheet1.cell(index_line, 5).value)
                                                    cell_time = str(worksheet1.cell(index_line, 6).value)
                                                    cell_recording = str(f'{cell_date}{cell_month}')
                                                    if str(date_for_recording) == str(cell_recording):
                                                        return bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                                    else:
                                                        break
                                            else:
                                                break
                                    else:
                                        break
                            else:
                                bot.send_message(message.chat.id, 'Это вся информация, что я нашел')
                                break
            Busy_recording()




    except ValueError:
        bot.send_message(message.chat.id, 'Что-то пошло не так, попробуйте еще раз!')


def Busy_dates1(message): #Проверить записи на число/второй лист
    busy_date = message.text
    try:
        if int(busy_date) <= 31:
            bot.send_message(message.chat.id, 'Придётся немного подождать, пока я все проверю :)')
            def Busy_recording():
                recording_user = int((worksheet1.cell(1, 1).value))
                recording_user1 = recording_user + 1
                if recording_user == None:
                    recording_user = 0
                else:
                    date_for_recording = f'{busy_date}{worksheet_list2}'
                    index_line = 2
                    cell_date = worksheet1.cell(index_line, 4).value
                    cell_month = str(worksheet1.cell(index_line, 5).value)
                    cell_time = str(worksheet1.cell(index_line, 6).value)
                    cell_recording = str(f'{cell_date}{cell_month}')

                    if str(date_for_recording) == str(cell_recording):
                        bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                        while True:
                            if index_line <= recording_user1:  # Нельзя проходить больше строк, чем записанное колличество людей
                                while True:
                                    index_line += 1
                                    cell_date = worksheet1.cell(index_line, 4).value
                                    cell_month = str(worksheet1.cell(index_line, 5).value)
                                    cell_time = str(worksheet1.cell(index_line, 6).value)
                                    cell_recording = str(f'{cell_date}{cell_month}')
                                    if str(date_for_recording) == str(cell_recording):
                                        bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                        while True:
                                            index_line += 1
                                            cell_date = worksheet1.cell(index_line, 4).value
                                            cell_month = str(worksheet1.cell(index_line, 5).value)
                                            cell_time = str(worksheet1.cell(index_line, 6).value)
                                            cell_recording = str(f'{cell_date}{cell_month}')
                                            if str(date_for_recording) == str(cell_recording):
                                                bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                                while True:
                                                    index_line += 1
                                                    cell_date = worksheet1.cell(index_line, 4).value
                                                    cell_month = str(worksheet1.cell(index_line, 5).value)
                                                    cell_time = str(worksheet1.cell(index_line, 6).value)
                                                    cell_recording = str(f'{cell_date}{cell_month}')
                                                    if str(date_for_recording) == str(cell_recording):
                                                        return bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                                    else:
                                                        break
                                            else:
                                                break
                                    else:
                                        break
                            else:
                                break
                    elif str(date_for_recording) != str(cell_recording):
                        while True:
                            if index_line <= recording_user1:  # Нельзя проходить больше строк, чем записанное колличество людей
                                while True:
                                    index_line += 1
                                    cell_date = worksheet1.cell(index_line, 4).value
                                    cell_month = str(worksheet1.cell(index_line, 5).value)
                                    cell_time = str(worksheet1.cell(index_line, 6).value)
                                    cell_recording = str(f'{cell_date}{cell_month}')
                                    if str(date_for_recording) == str(cell_recording):
                                        bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                        while True:
                                            index_line += 1
                                            cell_date = worksheet1.cell(index_line, 4).value
                                            cell_month = str(worksheet1.cell(index_line, 5).value)
                                            cell_time = str(worksheet1.cell(index_line, 6).value)
                                            cell_recording = str(f'{cell_date}{cell_month}')
                                            if str(date_for_recording) == str(cell_recording):
                                                bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                                while True:
                                                    index_line += 1
                                                    cell_date = worksheet1.cell(index_line, 4).value
                                                    cell_month = str(worksheet1.cell(index_line, 5).value)
                                                    cell_time = str(worksheet1.cell(index_line, 6).value)
                                                    cell_recording = str(f'{cell_date}{cell_month}')
                                                    if str(date_for_recording) == str(cell_recording):
                                                        return bot.send_message(message.chat.id, f'На {cell_month} месяц {cell_date} число забронированно время: {cell_time}')
                                                    else:
                                                        break
                                            else:
                                                break
                                    else:
                                        break
                            else:
                                bot.send_message(message.chat.id, 'Это вся информация, что я нашел')
                                break

            Busy_recording()

    except ValueError:
        bot.send_message(message.chat.id, 'Что-то пошло не так, попробуйте еще раз!')




@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    chat_id = call.message.chat.id


    if call.data == "Yes": # Перезапись, после кнопки "Да"
        # удаляем нужную запись по номеру в  строке
        worksheet1.delete_rows(*overwrite_user[chat_id]) #Внутри значение слоавря с номером ячейки
        recording_user = int((worksheet1.cell(1, 1).value))-1
        worksheet1.update_cell(1, 1, recording_user) # Убавляем колличество людей на 1
        bot.send_message(call.message.chat.id, 'Нажмите записаться и следуйте дальнейшим инструкциям')
        welcome(call.message)

    elif call.data == 'No': # Перезапись после кнопки нет
        bot.send_message(call.message.chat.id, 'Вас понял, всего хорошего!')

    # Кнопки времени и проверки даты на занятость
    elif call.data == 'first_month': #Проверка на первый месяц
        bot.send_message(call.message.chat.id,'Какая дата вас интересует? \nПросьба не вводить число больше, \nчем колличество дней в этом месяце')
        bot.register_next_step_handler(call.message, Busy_dates)

    elif call.data == 'second_month': #Проверка на второй месяц
        bot.send_message(call.message.chat.id,'Какая дата вас интересует? \nПросьба не вводить число больше, \nчем колличество дней в этом месяце')
        bot.register_next_step_handler(call.message, Busy_dates1)


    elif call.data == "first_sheet": #Запись на месяц с первого листа
        user_worksheet_list[chat_id] = [0] #Добавляем в словарь название месяца с первого листа, потом будем использовать

        bot.send_message(call.message.chat.id, 'Как я могу к вам обращаться?')
        bot.register_next_step_handler(call.message, full_name)

    elif call.data == "second_sheet": #Запись на месяц со второго листа
        bot.send_message(call.message.chat.id, 'Как я могу к вам обращаться?')
        user_worksheet_list[chat_id] = [2] #Добавляем в словарь название месяца с первого листа, потом будем использовать
        bot.register_next_step_handler(call.message, full_name)



    elif call.data == 'time1':
        date = ''.join(map(str, user_date[chat_id])) #Переменная "ДАТА" находится в словаре, разворачиваем
        month_sheet = ''.join(map(str, user_worksheet_list[chat_id]))
        line_time1 = ''.join(map(str, user_time1[chat_id]))
        bot.send_message(call.message.chat.id, 'Одну минуту, проверю не занята ли дата и время')

        if month_sheet == '0':
            date_for_recording = f'{date}{worksheet_list}{line_time1}'  # Переданные 3 переменные для записи, меняется только месяц

        elif month_sheet == '2':
            date_for_recording = f'{date}{worksheet_list2}{line_time1}'

        def check_date():
            recording_user = int((worksheet1.cell(1, 1).value))
            if recording_user == None:
                recording_user = 0
            else:

                index_line = 2
                cell_date = worksheet1.cell(index_line, 4).value
                cell_month = str(worksheet1.cell(index_line, 5).value)
                cell_time = str(worksheet1.cell(index_line, 6).value)
                cell_recording = str(f'{cell_date}{cell_month}{cell_time}')

                if str(date_for_recording) == str(cell_recording):
                    bot.send_message(call.message.chat.id, 'Запись на данную дату и время уже существует, \nпопробуйте выбрать другое время')
                else:
                    while True:
                        index_line +=1
                        recording_user1 = recording_user + 1
                        if index_line <= recording_user1:  # Нельзя проходить больше строк, чем записанное колличество людей
                            cell_date = worksheet1.cell(index_line, 4).value
                            cell_month = str(worksheet1.cell(index_line, 5).value)
                            cell_time = str(worksheet1.cell(index_line, 6).value)
                            cell_recording = str(f'{cell_date}{cell_month}{cell_time}')
                            while True:
                                if str(date_for_recording) == str(cell_recording):
                                    return bot.send_message(call.message.chat.id, 'Запись на данную дату и время уже существует, \nпопробуйте выбрать другое время')
                                else:
                                    break
                        else:
                            if month_sheet == '0': # Если прошло проверку, то ставим с нужным месяцем
                                bot.send_message(call.message.chat.id, f'Сделали вам запись на \n{worksheet_list} месяц, {date} число, время: {line_time1}')
                            elif month_sheet == '2':
                                bot.send_message(call.message.chat.id, f'Сделали вам запись на \n{worksheet_list2} месяц, {date} число, время: {line_time1}')
                            def save():
                                recording_user = int((worksheet1.cell(1, 1).value))
                                recording_user1 = recording_user + 1
                                recording_user2 = recording_user1 + 1
                                worksheet1.update_cell(1, 1, recording_user1)
                                worksheet1.update_cell(recording_user2, 1, recording_user1)
                                worksheet1.update_cell(recording_user2, 2, *user_name[chat_id])
                                worksheet1.update_cell(recording_user2, 3, *user_number[chat_id])
                                worksheet1.update_cell(recording_user2, 4, *user_date[chat_id])

                                if month_sheet == '0':  # Если прошло проверку, то ставим с нужным месяцем
                                    worksheet1.update_cell(recording_user2, 5, worksheet_list)
                                elif month_sheet == '2':
                                    worksheet1.update_cell(recording_user2, 5, worksheet_list2)

                                worksheet1.update_cell(recording_user2, 6, *user_time1[chat_id])

                            save()
                            keyboard3 = types.InlineKeyboardMarkup()

                            # Cделаем напоминалку, она сработает по времени за день до и поставим на таймер
                            item8 = types.InlineKeyboardButton(text='Да!', callback_data='09:00')  # кнопка на первое время в эту дату
                            keyboard3.add(item8)

                            item9 = types.InlineKeyboardButton(text='Не стоит...', callback_data='no_timer')  # кнопка на второе время в эту дату
                            keyboard3.add(item9)

                            bot.send_message(call.message.chat.id, text='Напомнить вам о записи заранее?',reply_markup=keyboard3)
                            break
        check_date()


    elif call.data == 'time2':
        date = ''.join(map(str, user_date[chat_id]))
        month_sheet = ''.join(map(str, user_worksheet_list[chat_id]))
        line_time2 = ''.join(map(str, user_time2[chat_id]))
        bot.send_message(call.message.chat.id, 'Одну минуту, проверю не занята ли дата и время')

        if month_sheet == '0':
            date_for_recording = f'{date}{worksheet_list}{line_time2}'  # Переданные 3 переменные для записи, меняется только месяц

        elif month_sheet == '2':
            date_for_recording = f'{date}{worksheet_list2}{line_time2}'


        def check_date():
            recording_user = int((worksheet1.cell(1, 1).value))
            if recording_user == None:
                recording_user = 0
            else:
                date_for_recording = f'{date}{worksheet_list}{line_time2}'  # Переданные 3 переменные для записи
                index_line = 2
                cell_date = worksheet1.cell(index_line, 4).value
                cell_month = str(worksheet1.cell(index_line, 5).value)
                cell_time = str(worksheet1.cell(index_line, 6).value)
                cell_recording = str(f'{cell_date}{cell_month}{cell_time}')

                if str(date_for_recording) == str(cell_recording):
                    bot.send_message(call.message.chat.id,'Запись на данную дату и время уже существует, \nпопробуйте выбрать другое время')

                else:
                    while True:
                        index_line += 1
                        recording_user1 = recording_user + 1
                        if index_line <= recording_user1:  # Нельзя проходить больше строк, чем записанное колличество людей
                            cell_date = worksheet1.cell(index_line, 4).value
                            cell_month = str(worksheet1.cell(index_line, 5).value)
                            cell_time = str(worksheet1.cell(index_line, 6).value)
                            cell_recording = str(f'{cell_date}{cell_month}{cell_time}')
                            while True:
                                if str(date_for_recording) == str(cell_recording):
                                    return bot.send_message(call.message.chat.id, 'Запись на данную дату и время уже существует, \nпопробуйте выбрать другое время')
                                else:
                                    break
                        else:
                            if month_sheet == '0': # Если прошло проверку, то ставим с нужным месяцем
                                bot.send_message(call.message.chat.id, f'Сделали вам запись на \n{worksheet_list} месяц, {date} число, время: {line_time2}')
                            elif month_sheet == '2':
                                bot.send_message(call.message.chat.id, f'Сделали вам запись на \n{worksheet_list2} месяц, {date} число, время: {line_time2}')

                            def save():
                                recording_user = int((worksheet1.cell(1, 1).value))
                                recording_user1 = recording_user + 1
                                recording_user2 = recording_user1 + 1
                                worksheet1.update_cell(1, 1, recording_user1)
                                worksheet1.update_cell(recording_user2, 1, recording_user1)
                                worksheet1.update_cell(recording_user2, 2, *user_name[chat_id])
                                worksheet1.update_cell(recording_user2, 3, *user_number[chat_id])
                                worksheet1.update_cell(recording_user2, 4, *user_date[chat_id])

                                if month_sheet == '0':  # Если прошло проверку, то ставим с нужным месяцем
                                    worksheet1.update_cell(recording_user2, 5, worksheet_list)
                                elif month_sheet == '2':
                                    worksheet1.update_cell(recording_user2, 5, worksheet_list2)

                                worksheet1.update_cell(recording_user2, 6, *user_time2[chat_id])

                            save()
                            keyboard3 = types.InlineKeyboardMarkup()

                            # Cделаем напоминалку, она сработает по времени за день до и поставим на таймер
                            item8 = types.InlineKeyboardButton(text='Да!', callback_data='11:30')  # кнопка на первое время в эту дату
                            keyboard3.add(item8)

                            item9 = types.InlineKeyboardButton(text='Не стоит...', callback_data='no_timer')  # кнопка на второе время в эту дату
                            keyboard3.add(item9)

                            bot.send_message(call.message.chat.id, text='Напомнить вам о записи заранее?', reply_markup=keyboard3)
                            break
        check_date()


    elif call.data == 'time3':
        date = ''.join(map(str, user_date[chat_id]))
        month_sheet = ''.join(map(str, user_worksheet_list[chat_id]))
        line_time3 = ''.join(map(str, user_time3[chat_id]))
        bot.send_message(call.message.chat.id, 'Одну минуту, проверю не занята ли дата и время')

        if month_sheet == '0':
            date_for_recording = f'{date}{worksheet_list}{line_time3}'  # Переданные 3 переменные для записи, меняется только месяц

        elif month_sheet == '2':
            date_for_recording = f'{date}{worksheet_list2}{line_time3}'

        def check_date():
            recording_user = int((worksheet1.cell(1, 1).value))

            if recording_user == None:
                recording_user = 0
            else:
                date_for_recording = f'{date}{worksheet_list}{line_time3}'  # Переданные 3 переменные для записи
                index_line = 2
                cell_date = worksheet1.cell(index_line, 4).value
                cell_month = str(worksheet1.cell(index_line, 5).value)
                cell_time = str(worksheet1.cell(index_line, 6).value)
                cell_recording = str(f'{cell_date}{cell_month}{cell_time}')

                if str(date_for_recording) == str(cell_recording):
                    bot.send_message(call.message.chat.id, 'Запись на данную дату и время уже существует, \nпопробуйте выбрать другое время')

                else:
                    while True:
                        index_line += 1
                        recording_user1 = recording_user + 1
                        if index_line <= recording_user1:  # Нельзя проходить больше строк, чем записанное колличество людей
                            cell_date = worksheet1.cell(index_line, 4).value
                            cell_month = str(worksheet1.cell(index_line, 5).value)
                            cell_time = str(worksheet1.cell(index_line, 6).value)
                            cell_recording = str(f'{cell_date}{cell_month}{cell_time}')
                            while True:
                                if str(date_for_recording) == str(cell_recording):
                                    return bot.send_message(call.message.chat.id, 'Запись на данную дату и время уже существует, \nпопробуйте выбрать другое время')
                                else:
                                    break
                        else:
                            if month_sheet == '0': # Если прошло проверку, то ставим с нужным месяцем
                                bot.send_message(call.message.chat.id, f'Сделали вам запись на \n{worksheet_list} месяц, {date} число, время: {line_time3}')
                            elif month_sheet == '2':
                                bot.send_message(call.message.chat.id, f'Сделали вам запись на \n{worksheet_list2} месяц, {date} число, время: {line_time3}')

                            def save():
                                recording_user = int((worksheet1.cell(1, 1).value))
                                recording_user1 = recording_user + 1
                                recording_user2 = recording_user1 + 1
                                worksheet1.update_cell(1, 1, recording_user1)
                                worksheet1.update_cell(recording_user2, 1, recording_user1)
                                worksheet1.update_cell(recording_user2, 2, *user_name[chat_id])
                                worksheet1.update_cell(recording_user2, 3, *user_number[chat_id])
                                worksheet1.update_cell(recording_user2, 4, *user_date[chat_id])

                                if month_sheet == '0':  # Если прошло проверку, то ставим с нужным месяцем
                                    worksheet1.update_cell(recording_user2, 5, worksheet_list)
                                elif month_sheet == '2':
                                    worksheet1.update_cell(recording_user2, 5, worksheet_list2)

                                worksheet1.update_cell(recording_user2, 6, *user_time3[chat_id])

                            save()
                            keyboard3 = types.InlineKeyboardMarkup()

                            # Cделаем напоминалку, она сработает по времени за день до и поставим на таймер
                            item8 = types.InlineKeyboardButton(text='Да!', callback_data='14:30')  # кнопка на первое время в эту дату
                            keyboard3.add(item8)

                            item9 = types.InlineKeyboardButton(text='Не стоит...', callback_data='no_timer')  # кнопка на второе время в эту дату
                            keyboard3.add(item9)

                            bot.send_message(call.message.chat.id, text='Напомнить вам о записи заранее?', reply_markup=keyboard3)
                            break

        check_date()


    elif call.data == '09:00': # Делаем это для передачи времени в таймер, чтобы напомнить человеку
        timer = call.data
        bot.send_message(call.message.chat.id, 'Введите число, чтобы я мог напомнить вам заранее')
        bot.register_next_step_handler(call.message, recording,timer)

    elif call.data == '11:30': # Делаем это для передачи времени в таймер, чтобы напомнить человеку
        timer = call.data
        bot.send_message(call.message.chat.id, 'Введите число, чтобы я мог напомнить вам заранее')
        bot.register_next_step_handler(call.message, recording,timer)

    elif call.data == '14:30': # Делаем это для передачи времени в таймер, чтобы напомнить человеку
        timer = call.data
        bot.send_message(call.message.chat.id, 'Введите число, чтобы я мог напомнить вам заранее')
        bot.register_next_step_handler(call.message, recording,timer)

    elif call.data == 'no_timer':
        bot.send_message(call.message.chat.id, 'Вас понял!')

    elif call.data == call.data: #Кнопка опознаёт цифру с календаря и передаёт её в дату
        date_number = call.data
        line_time = str(worksheet.cell(date_number, 3).value)
        if line_time == '-':
            bot.send_message(call.message.chat.id, 'К сожалению запись на данную дату отсутствует')
        else:
            bot.send_message(call.message.chat.id, f'{date_number} число, все верно? \nЕсли нет, то выберете другое число, нажав на него')
            bot.register_next_step_handler(call.message, full_date, date_number)



    else:
        bot.send_message(call.message.chat.id, 'не понимаю о чём вы ¯\_(ツ)_/¯')

while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
        time.sleep(30)
