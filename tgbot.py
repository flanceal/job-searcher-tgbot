import db_handler
import telebot
from telebot import types
from job_scraper import DjinniScrapper
from db_handler import get_from_settings

# api token of telegram bot
API_TOKEN = '5909806725:AAGOPdC46PWSwotsRRtsAo8wzucs4AAWYyU'

# define telegram bot instance
bot = telebot.TeleBot(API_TOKEN)


"""
Handlers for messages
"""


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    # initialise new user in database table
    db_handler.init_new_user(message)
    main_menu(message)


# Main menu keyboard and 'Back' keyword handler
@bot.message_handler(func=lambda message: 'Back' in message.text)
def main_menu(message):
    text = 'You are in the main menu. Choose selection'
    # Keyboard for main menu of bot
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Search for jobs'
    button2 = 'Always search'
    button3 = 'Settings'
    markup.row(button1, button2)
    markup.row(button3)

    bot.send_message(message.chat.id, text, reply_markup=markup)


# always search keywords handler (comment and document later)
@bot.message_handler(func=lambda message: 'Search for jobs' in message.text)
def search_handler(message):
    search_jobs(message)


# always search keywords handler (comment and document later)
@bot.message_handler(func=lambda message: 'Always search' in message.text)
def always_search_settings_handler(message):
    text = "Choose settings"
    markup = always_search_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# settings and back keywords handler
@bot.message_handler(func=lambda message: message.text in ['Settings', 'Settings menu'])
def settings_handler(message):
    # Get the user's settings from the database
    specialisation, experience, location, salary = get_from_settings(message.chat.id, 'specialisation', 'experience',
                                                                     'onsite_remote', 'salary')

    # Construct the text of the reply message
    text = f"""Your settings:\nSpecialisation: {specialisation} \nExperience: {experience}\nOn-site/Remote:
    {location} Salary settings: {salary}
    """
    markup = settings_keyboard()

    # Send the reply message to the user
    bot.send_message(message.chat.id, text, reply_markup=markup)


# specialisation keyword handler
@bot.message_handler(func=lambda message: 'Specialisation' in message.text)
def specialisation_handler(message):
    text = 'Choose specialisation'

    # Create keyboard with specialisation parameters for the user
    markup = specialisation_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# experience keyword handler
@bot.message_handler(func=lambda message: 'Experience' in message.text)
def experience_handler(message):
    text = 'Choose experience'

    # Create keyboard with experience parameters for the user
    markup = experience_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


#  on-site/remote keyword handle
@bot.message_handler(func=lambda message: 'On-site/Remote' in message.text)
def onsite_remote_handler(message):
    text = 'Choose type'

    # Create keyboard with on-site/remote parameters for the user
    markup = onsite_remote_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# salary keyword handle
@bot.message_handler(func=lambda message: 'Salary settings' in message.text)
def salary_handler(message):
    text = 'Choose settings'

    # Create keyboard with salary parameters for the user
    markup = salary_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# detailed salary keywords handle
@bot.message_handler(func=lambda message: message.text in ['Public salary', 'with a disclosed/public salary'])
def public_salary_handler(message):
    # Insert the chosen salary setting into the database
    db_handler.insert_into_settings(message, 'salary')
    text = f"Salary set to {message.text}"
    bot.send_message(message.chat.id, text)
    settings_handler(message)

"""
Searching functions
"""


def search_jobs(message):
    for appropriate_job in compare_jobs(message):
        text = show_jobs(appropriate_job)
        bot.send_message(message.chat.id, text)


def compare_jobs(message):
    experiences = {"0-1 years": ["Без досвіду", 1],
                   "1-2 years": [1, 2],
                   "2-3 years": [2, 3],
                   '3-5 years': [3, 5]}
    # Get the user's settings from the database
    specialisation, location, salary = get_from_settings(message.chat.id, 'specialisation',
                                                                     'onsite_remote', 'salary')
    experience = experiences.get(get_from_settings(message.chat.id, 'experience')[0])
    for job in DjinniScrapper(specialisation).search_jobs():
        print(f"Job: {(job.experience)}")
        print(f"User: {experience}")
        print(f"Job: {location}")
        print(f"User: {location}")

        if salary == 'with a disclosed/public salary':
            if int(job.experience) in experience and job.location == location:
                print('hello world')
                yield job
        else:
            if job.experience in experience and job.location == location and job.salary:
                print('hello world')
                yield job


def show_jobs(job):
    text = f"""
    Job has been found:
    {job.title}\nCompany: {job.company}\nRequired experience: {job.experience} years of experience\n
    Location: {job.location}
    """
    if job.salary:
        text += f"\Salary: {job.salary}"
    return text


"""
Settings keywords handlers
"""
# lists of choices for user settings used in the Telegram bot.
specialisations = ['Front-End(JavaScript)', 'Java', 'C#/.NET', 'Python', 'Flutter', 'Python', 'PHP', 'Node.js',
             'IOS', 'Android', 'C++']

experiences_choices = ['No Experience', '1-2 years', '2-3 years', '3-5 years']
onsite_remote_choices = ['Remote', 'On-site', 'Settings menu']
salary_choices = ['Public salary', 'with a disclosed/public salary']


# Handle all settings keywords with one function
@bot.message_handler(func=lambda message: message.text in specialisations + experiences_choices + onsite_remote_choices
                                          + salary_choices)
def set_setting(message):
    # Identify the type of setting based on the user's input
    setting_type = None
    if message.text in specialisations:
        setting_type = 'specialisation'
    elif message.text in experiences_choices:
        setting_type = 'experience'
    elif message.text in onsite_remote_choices:
        setting_type = 'onsite_remote'
    elif message.text in salary_choices:
        setting_type = 'salary'

    # If a valid setting type is identified, insert the setting into the database and send a message back to the user
    if setting_type is not None:
        result = db_handler.insert_into_settings(message, setting_type)
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
    button1 = '0-1 years'
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


bot.infinity_polling()
