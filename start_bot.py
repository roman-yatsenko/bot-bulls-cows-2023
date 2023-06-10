import random
import string

import telebot

from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
guessed_number = ''


@bot.message_handler(commands=['start', 'game'])
def start_game(message):
    digits = [s for s in string.digits]
    global guessed_number
    guessed_number = ''
    for pos in range(4):
        if pos:
            digit = random.choice(digits)
        else:
            digit = random.choice(digits[1:])
        guessed_number += digit
        digits.remove(digit)
    bot.reply_to(message, f'Я загадав 4-значне число. Спробуй відгадати, {message.from_user.first_name}!')


if __name__ == '__main__':
    print('Bot works!')
    bot.polling(non_stop=True)
