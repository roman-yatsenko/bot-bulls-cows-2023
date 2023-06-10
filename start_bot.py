import random
import string

import telebot

from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
guessed_number = ''
tries = -1 # tries == -1, якщо гра не активна


@bot.message_handler(commands=['start', 'game'])
def start_game(message):
    digits = [s for s in string.digits]
    global guessed_number, tries
    guessed_number = ''
    for pos in range(4):
        if pos:
            digit = random.choice(digits)
        else:
            digit = random.choice(digits[1:])
        guessed_number += digit
        digits.remove(digit)
    print(guessed_number)
    tries = 0
    bot.reply_to(message, 'Гра "Бики та корови"\n'
        f'Я загадав 4-значне число. Спробуй відгадати, {message.from_user.first_name}!')

@bot.message_handler(commands=['help'])
def show_help(message):
    bot.reply_to(message, """
Гра "Бики та корови"

Гра, в якій потрібно за декілька спроб вгадати 4-значне число, яке загадав бот. Після кожної спроби бот повідомляя кількість вгаданих цифр, ще не на "своїх" місцях ("корови"), та повних цифрових співпадінь ("бики")
""")

@bot.message_handler(content_types=['text'])
def bot_answer(message):
    global tries
    text = message.text
    if len(text) == 4 and text.isnumeric() and len(text) == len(set(text)):
        bulls, cows = get_bulls_cows(text, guessed_number)
        tries += 1
        if bulls != 4:
            response = f'Бики: {bulls} | Корови: {cows} ({tries} спроба)'
        else:
            response = f'Ти вгадав за {tries} спроб! Зіграємо ще?'
            bot.send_message(message.from_user.id, response, reply_markup=get_restart_buttons())
            tries = -1
            return
    else:
        response = 'Надішли мені 4-значне число з різними цифрами!'
    bot.send_message(message.from_user.id, response)

def get_restart_buttons():
    buttons = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    buttons.add('Так', 'Ні')
    return buttons

def get_bulls_cows(text1, text2):
    bulls = cows = 0
    for i in range(4):
        if text1[i] in text2:
            if text1[i] == text2[i]:
                bulls += 1
            else:
                cows += 1
    return bulls, cows

if __name__ == '__main__':
    print('Bot works!')
    bot.polling(non_stop=True)
