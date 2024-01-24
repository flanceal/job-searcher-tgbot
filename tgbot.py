import db_handler
import telebot
from time import sleep
from telebot import types
from DjinniScraper import DjinniScrapper
from db_handler import get_from_settings


# api token of telegram bot
API_TOKEN = '6248629109:AAHENOf8Wcc1CDB8NCkBQuVkhKcfhVndy4k'

# define telegram bot instance
bot = telebot.TeleBot(API_TOKEN)

# Handlers for messages


# Handle '/start' and '/help'
# This function is triggered when a user sends commands like '/start' or '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    greeting_message = """
    <b>Hello! Welcome to the Bot! 😊</b>

    I am here to assist you in finding jobs that match your preferences. 
    Feel free to explore and customize your job search settings.

    <b>Here are some options you can choose:</b>
    - Search for jobs 🔍
    - Activate "Always search" mode 🔄
    - Configure settings ⚙️

    Let me know how I can help you! 🤖
    """
    # initialise new user in database table
    print(f"User Id: {message.chat.id}")
    db_handler.init_new_user(message)
    bot.send_message(message.chat.id, text=greeting_message, parse_mode='HTML')
    main_menu(message)


# back keyword handler
# This function is triggered when a message contains the text 'Back'
@bot.message_handler(func=lambda message: 'Back' in message.text)
def main_menu(message):
    text = '👋 Welcome to the main menu. Please make your selection.'

    # Keyboard for the main menu of the bot
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Search for jobs 🕵️‍♂️'
    button2 = 'Always search 🔍'
    button3 = 'Settings ⚙️'
    markup.row(button1, button2)
    markup.row(button3)

    bot.send_message(message.chat.id, text, reply_markup=markup)


# search for jobs keyword handler
# This function checks if the user has specified a job specialization in their settings.
# If a specialization is specified, it sends a search settings keyboard to the user.
# If no specialization is specified, it sends a specialization selection keyboard to the user.
@bot.message_handler(func=lambda message: 'Search for jobs 🕵️‍♂️' in message.text)
def search_handler(message):
    if get_from_settings(message.chat.id, 'specialisation')[0]:
        markup = search_keyboard()
        bot.send_message(message.chat.id, 'Please choose your search settings', reply_markup=markup)
    else:
        markup = specialisation_keyboard()
        text = "Oops! 😕 It looks like you haven't specified your preferred job specialisation yet. " \
            "Please set your specialisation first"
        bot.send_message(message.chat.id, text, reply_markup=markup)


# always search keywords handler (comment and document later)
# This function updates the search status in the database based on the user's selection.
# If the user chooses to enable search, it updates the search status to True and calls the search_jobs function.
# If the user chooses to disable search, it updates the search status to False and sends a message indicating that
# the search has been stopped.
@bot.message_handler(func=lambda message: message.text in ['Enable search', 'Disable search'])
def search_settings_handler(message):
    if message.text == 'Enable search':
        # Update search status to True in the database
        db_handler.update_search_status(message.chat.id, 'search_status', True)
        # Call the search_jobs function with the second argument set to False
        search_jobs(message, False)
    else:
        # Update search status to False in the database
        db_handler.update_search_status(message.chat.id, 'search_status', False)
        # Send a message indicating that the search has been stopped
        bot.send_message(message.chat.id, "Search has been stopped")


# always search keywords handler
@bot.message_handler(func=lambda message: 'Always search 🔍' in message.text)
def always_search_settings_handler(message):
    if get_from_settings(message.chat.id, 'specialisation')[0]:
        text = "Please choose your always search settings."
        markup = always_search_keyboard()

        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        markup = specialisation_keyboard()
        text = "Oops! 😕 It looks like you haven't specified your preferred job specialisation yet. " \
            "Please set your specialisation first"
        bot.send_message(message.chat.id, text, reply_markup=markup)


# enable always search keyword handler
# Enable always search handler
@bot.message_handler(func=lambda message: 'Enable always search' in message.text)
def always_search_settings_handler(message):
    # Change always search status into True
    db_handler.update_search_status(message.chat.id, 'always_search_status', True)
    # Send activation message
    bot.send_message(message.chat.id, "Always search has been activated."
                                      "I will continuously search for new job opportunities.")
    main_menu(message)

    # Perform job searches while always search is enabled
    while db_handler.get_user_search_status(message.chat.id, 'always_search_status'):
        search_jobs(message, True)
        sleep(120)
        print('working')


# Disable always search handler
@bot.message_handler(func=lambda message: 'Disable always search' in message.text)
def always_search_settings_handler(message):
    # Change always search status into False
    db_handler.update_search_status(message.chat.id, 'always_search_status', False)
    # Send deactivation message
    bot.send_message(message.chat.id, "Always search has been stopped."
                                      " I will no longer search for new job opportunities automatically.")
    # Return to the main menu
    main_menu(message)


# settings keywords handler
@bot.message_handler(func=lambda message: message.text in ['Settings ⚙️', 'Settings menu'])
def settings_handler(message):
    # Get the user's settings from the database
    specialisation, experience, location, salary = get_from_settings(message.chat.id, 'specialisation', 'experience',
                                                                     'onsite_remote', 'salary')

    # Construct the text of the reply message with HTML formatting
    text = f"""⚙️ Your settings:
    <b>Specialisation:</b> {specialisation} 
    <b>Experience:</b> {experience}
    <b>On-site/Remote:</b> {location}
    <b>Salary settings:</b> {salary}"""

    markup = settings_keyboard()

    # Send the reply message to the user
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')


# specialisation keyword handler
@bot.message_handler(func=lambda message: 'Specialisation' in message.text)
def specialisation_handler(message):
    text = 'Please choose your specialisation.'

    # Create keyboard with specialisation parameters for the user
    markup = specialisation_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# experience keyword handler
@bot.message_handler(func=lambda message: 'Experience' in message.text)
def experience_handler(message):
    text = 'Please choose your experience.'

    # Create keyboard with experience parameters for the user
    markup = experience_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


#  on-site/remote keyword handle
@bot.message_handler(func=lambda message: 'On-site/Remote' in message.text)
def onsite_remote_handler(message):
    text = 'Please choose your workplace preferences: On-site or Remote? 🏢💻"'

    # Create keyboard with on-site/remote parameters for the user
    markup = onsite_remote_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# salary keyword handle
@bot.message_handler(func=lambda message: 'Salary settings' in message.text)
def salary_handler(message):
    text = 'Please choose your workplace preferences: Public salary or with a disclosed/public salary? 💸'

    # Create keyboard with salary parameters for the user
    markup = salary_keyboard()

    bot.send_message(message.chat.id, text, reply_markup=markup)


# detailed salary keywords handle
@bot.message_handler(func=lambda message: message.text in ['Public salary', 'with a disclosed/public salary'])
def public_salary_handler(message):
    # Insert the chosen salary setting into the database
    db_handler.insert_into_settings(message, 'salary')
    text = f"Salary preferences set to {message.text} ✅"
    bot.send_message(message.chat.id, text)
    settings_handler(message)


# Searching functions


def search_jobs(message, always_search=False):
    """
    Search for jobs based on user's settings and send them as messages to the user.

    Args:
        message (telegram.Message): The message object containing user information.
        always_search: Specifies whether to send a message if no matching jobs are found while comparing jobs in
            compare jobs function

    Returns:
        None
    """
    for job in compare_jobs(message, always_search):
        search_status = db_handler.get_user_search_status(message.chat.id, 'search_status')[0][0]
        always_search_status = db_handler.get_user_search_status(message.chat.id, 'always_search_status')[0][0]
        if not search_status and not always_search:
            break
        elif not always_search_status and always_search:
            break
        text = show_jobs(job)

        # button for job link under the message
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='See details', url=job.link)
        markup.add(button)

        # Insert shown job into seen_jobs table
        db_handler.insert_seen_job(message.chat.id, job.title, job.specialisation,
                                   job.company, job.experience, job.location, job.link)
        bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
        sleep(1)


def compare_jobs(message, always_search=False):
    """
    Compare jobs from web scraping with user's settings and yield matching jobs.

    Args:
        message (telegram.Message): The message object containing user information.
        always_search (bool, optional): Specifies whether to send a message if no matching jobs are found.
            If set to True (default), a message will be sent. If set to False, no message will be sent.
    Yields:
        Job: A matching job object.

    Returns:
        None
    """
    print('new search')
    experiences = {"0-1 years": ["No experience", '1 year of experience'],
                   "1-2 years": ['1 year of experience', '2 years of experience'],
                   "2-3 years": ['2 years of experience', '3 роки досвіду'],
                   '3-5 years': ['3 years of experience', '5 years of experience'],
                   '5+ years': ['5 years of experience']}
    # Get the user's settings from the database
    specialisation, location, salary = get_from_settings(message.chat.id, 'specialisation', 'onsite_remote', 'salary')
    experience = experiences.get(get_from_settings(message.chat.id, 'experience')[0])

    # Monitor whether there is no matching jobs or all the jobs were seen
    found_jobs = False
    # Compare jobs attributes with user's criteria and check whether job is in 'seen_jobs' table in database
    for job in DjinniScrapper(specialisation).search_jobs():
        if is_matching_job(message, job, experience, location, specialisation, salary):
            found_jobs = True
            yield job

    # If no matching jobs were found
    if not found_jobs and not always_search:
        text = """Oops! 😕
        It seems that there are no matching jobs available at the moment or you have seen all the available jobs.
        Don't worry, new opportunities might arise soon!"""

        bot.send_message(message.chat.id, text)


def is_matching_job(message, job, experience, location, specialisation, salary):
    # Check if job experience matches the specified experience
    if experience and job.experience not in experience:
        return False

    # Check if job location matches the specified location
    if location and job.location != location:
        return False

    # Check if job has already been seen by the user for the specified specialisation
    if is_job_seen(message, job, specialisation):
        return False

    # Check if salary is set to 'Public salary' and the job has no salary information
    if salary == 'Public salary' and not job.salary:
        return False

    # Return True if all conditions pass
    return True


def is_job_seen(message, job, specialisation):
    """
    Check if a job has already been seen by the user.

    Args:
        message (telegram.Message): The message object containing user information.
        job (Job): The job object to check.
        specialisation (str): The specialisation of the job.

    Returns:
        bool: True if the job has already been seen, False otherwise.
    """
    for title, company, experience, location, link in db_handler.get_jobs(message.chat.id, specialisation):
        if job.title == title and job.company == company and job.experience == experience and job.link == link:
            return True
    return False


def show_jobs(job):
    """
    Create a text representation of a job.

    Args:
        job (Job): The job object to display.

    Returns:
        str: The formatted text representation of the job.
    """
    text = f"""
    <b>Job Found ✨</b>

    {job.title}
    Company: {job.company}
    Required Experience: {job.experience}
    Workplace: {job.location}
    """
    if job.salary:
        text += f"\nSalary: {job.salary}"

    return text


# Settings keywords handlers

# lists of choices for user settings used in the Telegram bot.
specialisations = ['Front-End(JavaScript)', 'Java', 'C#/.NET', 'Python', 'Flutter', 'Python', 'PHP', 'Node.js',
                   'IOS', 'Android', 'C++']

experiences_choices = ['0-1 years', '1-2 years', '2-3 years', '3-5 years', '5+ years', 'Any experience']
onsite_remote_choices = ['Remote', 'On-site', "Any workplace", 'Settings menu']
salary_choices = ['Public salary', 'with a disclosed/public salary']


# Handle all settings keywords with one function
@bot.message_handler(func=lambda message: message.text in specialisations + experiences_choices +
                                          onsite_remote_choices + salary_choices)
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


# Keyboards


# Keyboard for search
def search_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Enable search'
    button2 = 'Disable search'
    button5 = 'Back'

    markup.row(button1, button2)
    markup.row(button5)

    return markup


# Keyboard for always search
def always_search_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Enable always search'
    button2 = 'Disable always search'
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
    button5 = '5+ years'
    button6 = 'Any experience'
    button7 = 'Settings menu'

    markup.row(button1, button2, button3, button4)
    markup.row(button5, button6, button7)

    return markup


# On-site/Remote keyboard
def onsite_remote_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = 'Remote'
    button2 = 'On-site'
    button3 = 'Any workplace'
    button4 = 'Settings menu'

    markup.row(button1, button2)
    markup.row(button3, button4)

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
