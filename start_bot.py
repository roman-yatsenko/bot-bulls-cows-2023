import random
import string

import telebot

from config import BOT_TOKEN
from user import User, DEFAULT_USER_LEVEL, get_or_create_user, save_user, del_user


bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['mode'])
def select_mode(message):
    user = get_or_create_user(message.from_user.id)
    user.mode = ''
    user.reset()
    response = 'Гра "Бики та корови"\n' + \
               'Обери режим гри (хто загадує число)'
    bot.send_message(message.from_user.id, response, reply_markup=get_buttons('Бот', 'Юзер'))

@bot.message_handler(commands=['level'])
def select_level(message):
    user = get_or_create_user(message.from_user.id)
    user.reset()
    save_user(message.from_user.id, user)
    response = 'Гра "Бики та корови"\n' + \
               'Обери рівень (кількість цифр)'
    bot.send_message(message.from_user.id, response, reply_markup=get_buttons('3', '4', '5'))

@bot.message_handler(commands=['start', 'game'])
def start_game(message, level=None):
    user = get_or_create_user(message.from_user.id)
    if not user.mode:
        select_mode(message)
        return
    if level:
        user.level = level
    digits = [s for s in string.digits]
    guessed_number = ''
    for pos in range(user.level):
        if pos:
            digit = random.choice(digits)
        else:
            digit = random.choice(digits[1:])
        guessed_number += digit
        digits.remove(digit)
    print(f'{guessed_number} for {message.from_user.username}')
    user.reset(guessed_number)
    save_user(message.from_user.id, user)
    bot.reply_to(message, 'Гра "Бики та корови"\n'
        f'Я загадав {user.level}-значне число. Спробуй відгадати, {message.from_user.first_name}!')

@bot.message_handler(commands=['help'])
def show_help(message):
    bot.reply_to(message, """
Гра "Бики та корови"

Гра, в якій потрібно за декілька спроб вгадати 4-значне число, яке загадав бот. Після кожної спроби бот повідомляє кількість вгаданих цифр, ще не на "своїх" місцях ("корови"), та повних цифрових співпадінь ("бики")
""")

@bot.message_handler(content_types=['text'])
def bot_answer(message):
    user = get_or_create_user(message.from_user.id)
    if user.number:
        bot_answer_to_user_guess(message, user)
    else:
        bot_answer_not_in_game(message, user)

def bot_answer_not_in_game(message, user):
    text = message.text
    if text in ('3', '4', '5'):
        start_game(message, int(text))
        return
    elif text == 'Так':
        start_game(message, user.level)
        return
    elif not user.mode and text in ('Бот', 'Юзер'):
        if text == 'Бот':
            user.mode = 'bot'
        elif text == 'Юзер':
            user.mode = 'user'
        save_user(message.from_user.id, user)
        start_game(message, user.level)
        return
    else:
        response = 'Для запуску гри набери /start'
    bot.send_message(message.from_user.id, response)

def bot_answer_to_user_guess(message, user):
    text = message.text
    if len(text) == user.level and text.isnumeric() and len(text) == len(set(text)):
        bulls, cows = get_bulls_cows(text, user.number)
        user.tries += 1
        if bulls != user.level:
            response = f'Бики: {bulls} | Корови: {cows} ({user.tries} спроба)'
            save_user(message.from_user.id, user)
        else:
            response = f'Ти вгадав за {user.tries} спроб! Зіграємо ще?'
            user.reset()
            save_user(message.from_user.id, user)
            bot.send_message(message.from_user.id, response, 
                            reply_markup=get_buttons('Так', 'Ні'))
            return
    else:
        response = f'Надішли мені {user.level}-значне число з різними цифрами!'
    bot.send_message(message.from_user.id, response)

def get_buttons(*args):
    buttons = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    buttons.add(*args)
    return buttons

def get_bulls_cows(text1, text2):
    bulls = cows = 0
    for i in range(min(len(text1), len(text2))):
        if text1[i] in text2:
            if text1[i] == text2[i]:
                bulls += 1
            else:
                cows += 1
    return bulls, cows

if __name__ == '__main__':
    print('Bot works!')
    bot.polling(non_stop=True)
