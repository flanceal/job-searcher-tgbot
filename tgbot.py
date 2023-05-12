import db_handler
import telebot
from telebot import types
from db_handler import get_from_settings

API_TOKEN = '5909806725:AAGOPdC46PWSwotsRRtsAo8wzucs4AAWYyU'

bot = telebot.TeleBot(API_TOKEN)


"""
Handlers
"""


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    db_handler.init_new_user(message)
    text = 'You are in the main menu. Choose selection'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Search for jobs'
    button2 = 'Always search'
    button3 = 'Settings'
    markup.row(button1, button2)
    markup.row(button3)

    bot.send_message(message.chat.id, text, reply_markup=markup)


# always search keywords handler
@bot.message_handler(func=lambda message: 'Always search' in message.text)
def always_search_settings_handler(message):
    text = "Choose settings"
    markup = always_search_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# settings keyword handler
@bot.message_handler(func=lambda message: 'Settings' in message.text)
def settings_handler(message):
    settings = get_from_settings(message.chat.id, 'specialisation', 'experience', 'onsite_remote', 'salary')
    text = f"""Your settings:\nSpecialisation: {settings[0]} \nExperience: {settings[1]}\nOn-site/Remote: {settings[2]} 
    Salary settings: {settings[3]}
    """

    if get_from_settings(message.chat.id, 'salary')[0] == 'Public salary' and get_from_settings(message.chat.id,
                                                                                                'salary_from')[0]:
        text += f"\nSalary starts from: {get_from_settings(message.chat.id, 'salary_from')[0]}"
    markup = settings_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# specialisation keyword handle
@bot.message_handler(func=lambda message: 'Specialisation' in message.text)
def specialisation_handler(message):
    text = 'Choose specialisation'
    markup = specialisation_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# experience keyword handle
@bot.message_handler(func=lambda message: 'Experience' in message.text)
def experience_handler(message):
    text = 'Choose experience'
    markup = experience_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


#  on-site/remote keyword handle
@bot.message_handler(func=lambda message: 'On-site/Remote' in message.text)
def onsite_remote_handler(message):
    text = 'Choose type'
    markup = onsite_remote_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# salary keyword handle
@bot.message_handler(func=lambda message: 'Salary settings' in message.text)
def salary_handler(message):
    text = 'Choose settings'
    markup = salary_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# public salary keyword handle
@bot.message_handler(func=lambda message: message.text in ['Public salary', 'with a disclosed/public salary'])
def public_salary_handler(message):
    db_handler.insert_into_settings(message, 'salary')
    if message.text == 'Public salary':
        text = 'Salary starts from'
        markup = public_salary_settings()
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        settings_handler(message)


# back (main menu) keyword handle
@bot.message_handler(func=lambda message: 'Back' in message.text)
def back_to_main_menu(message):
    send_welcome(message)


# settings menu keyword handle
@bot.message_handler(func=lambda message: 'Settings menu' in message.text)
def back_to_settings(message):
    settings_handler(message)


"""
Settings keywords handlers
"""
languages_choices = ['Front-End(JavaScript)', 'Java', 'C#/.NET', 'Python', 'Flutter', 'Python', 'PHP', 'Node.js',
             'IOS', 'Android', 'C++']

experiences_choices = ['No Experience', '1-2 years', '2-3 years', '3-5 years']
onsite_remote_choices = ['Remote', 'On-site', 'Settings menu']
public_salary_choices = ['1500$', '2500$', '3500$', '4500$', '5500$', '6500$']


# insert specialisation into database user's settings
@bot.message_handler(func=lambda message: message.text in languages_choices)
def set_specialisation(message):
    result = db_handler.insert_into_settings(message, 'specialisation')
    bot.send_message(message.chat.id, result)
    settings_handler(message)


# insert experience into database user's settings
@bot.message_handler(func=lambda message: message.text in experiences_choices)
def set_experience(message):
    result = db_handler.insert_into_settings(message, 'experience')
    bot.send_message(message.chat.id, result)
    settings_handler(message)


# insert on-site/remote into database user's settings
@bot.message_handler(func=lambda message: message.text in onsite_remote_choices)
def set_onsite_remote(message):
    result = db_handler.insert_into_settings(message, 'onsite_remote')
    bot.send_message(message.chat.id, result)
    settings_handler(message)


# insert public salary into database user's settings
@bot.message_handler(func=lambda message: message.text in public_salary_choices)
def set_public_salary(message):
    result = db_handler.insert_into_settings(message, 'salary_from')
    bot.send_message(message.chat.id, result)
    settings_handler(message)


"""
Keyboards
"""


# Keyboard for always search
def always_search_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Start searching'
    button2 = 'Stop searching'
    button5 = 'Back'

    markup.row(button1, button2)
    markup.row(button5)

    return markup


# Keyboard for setting
def settings_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Specialisation'
    button2 = 'Experience'
    button3 = 'On-site/Remote'
    button4 = 'Salary settings'
    button5 = 'Back'
    markup.row(button1, button2)
    markup.row(button3, button4, button5)

    return markup


# Keyboard for specialisation
def specialisation_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Front-End(JavaScript)'
    button2 = 'Java'
    button3 = 'C#/.NET'
    button4 = 'Python'
    button5 = 'PHP'
    button6 = 'Node.js'
    button7 = 'IOS'
    button8 = 'Android'
    button9 = 'C++'
    button10 = 'Flutter'
    button11 = 'Settings menu'

    markup.row(button1, button2, button3, button4)
    markup.row(button5, button6, button7, button8)
    markup.row(button9, button10, button11)

    return markup


# Keyboard for experience
def experience_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'No Experience'
    button2 = '1-2 years'
    button3 = '2-3 years'
    button4 = '3-5 years'
    button5 = 'Settings menu'

    markup.row(button1, button2)
    markup.row(button3, button4, button5)

    return markup


# On-site/Remote keyboard
def onsite_remote_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Remote'
    button2 = 'On-site'
    button3 = 'Settings menu'

    markup.row(button1, button2)
    markup.row(button3)

    return markup


# salary keyboard
def salary_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Public salary'
    button2 = 'with a disclosed/public salary'
    button3 = 'Settings menu'

    markup.row(button1, button2)
    markup.row(button3)

    return markup


# public salary settings
def public_salary_settings():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = '1500$'
    button2 = '2500$'
    button3 = '3500$'
    button4 = '4500$'
    button5 = '5500$'
    button6 = '6500$'

    markup.row(button1, button2, button3)
    markup.row(button4, button5, button6)

    return markup


bot.infinity_polling()
