import psycopg2
import telebot
import pandas as pd
from psycopg2 import OperationalError
from datetime import datetime
from datetime import date
from telebot import types
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

discipline=""
date=""
description=""
deleting_process=0

def check_deadlines():
    refresh()
    print("deadlines checked", return_time())
    connection = create_connection(
        "d709i4msa5b0s2", "zggixxdwjxvkrq", "0b43a6f8cf9bef0b7b5fcf8b445d9cc3059159f81c56662fe64e50e9ad033542", "ec2-63-34-223-144.eu-west-1.compute.amazonaws.com", "5432"
    )
    return_time()
    select_deadlines = "SELECT * FROM deadlines ORDER BY deadline ASC"
    return execute_read_query(connection, select_deadlines)

def send_pic(id):
    refresh()
    pd.set_option('max_colwidth', 1000)
    engine = create_engine(
        'postgresql+psycopg2://zggixxdwjxvkrq:0b43a6f8cf9bef0b7b5fcf8b445d9cc3059159f81c56662fe64e50e9ad033542@ec2-63-34-223-144.eu-west-1.compute.amazonaws.com/d709i4msa5b0s2')
    df = pd.read_sql_table('deadlines', engine)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    pp = PdfPages("deadlines.pdf")
    pp.savefig(fig, bbox_inches='tight')
    pp.close()
    bot.send_document(chat_id = id, document = open("deadlines.pdf", 'rb'))

def add_deadline():
    print("deadline added", return_time())
    connection = create_connection(
        "d709i4msa5b0s2", "zggixxdwjxvkrq", "0b43a6f8cf9bef0b7b5fcf8b445d9cc3059159f81c56662fe64e50e9ad033542",
        "ec2-63-34-223-144.eu-west-1.compute.amazonaws.com", "5432"
    )
    connection.autocommit = True
    data_tuple = (discipline, description, date)
    print(data_tuple)
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO deadlines(discipline, task, deadline) VALUES {data_tuple}")

def delete_deadline(id):
    connection = create_connection(
        "d709i4msa5b0s2", "zggixxdwjxvkrq", "0b43a6f8cf9bef0b7b5fcf8b445d9cc3059159f81c56662fe64e50e9ad033542",
        "ec2-63-34-223-144.eu-west-1.compute.amazonaws.com", "5432"
    )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM deadlines WHERE id = {id}")
    print("deadline deleted", return_time())


def return_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

def refresh():
    connection = create_connection(
        "d709i4msa5b0s2", "zggixxdwjxvkrq", "0b43a6f8cf9bef0b7b5fcf8b445d9cc3059159f81c56662fe64e50e9ad033542",
        "ec2-63-34-223-144.eu-west-1.compute.amazonaws.com", "5432"
    )
    connection.autocommit = True
    select_deadlines = "SELECT * from deadlines WHERE deadline < CURRENT_DATE "
    dllist = execute_read_query(connection, select_deadlines)
    for dl in dllist:
        delete_deadline(dl[0])

def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query executed successfully")
    except OperationalError as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except OperationalError as e:
        print(f"The error '{e}' occurred")

bot = telebot.TeleBot("5209968243:AAESYZI7iVvt3jukJsU6jvixevWIPhekCG4")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('/add_deadline')
    itembtn2 = types.KeyboardButton('/check_deadlines')
    itembtn3 = types.KeyboardButton('/delete_deadlines')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Welcome to deadlines bot by @kroexov. Choose the starting option!", reply_markup=markup)

@bot.message_handler(commands=['add_deadline', 'check_deadlines', 'delete_deadlines', 'get_pdf'])
def send_welcome(message):
    if message.text == "/add_deadline":
        global discipline
        discipline = ""
        global date
        date = ""
        global description
        description = ""
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('Applied mathematics')
        itembtn2 = types.KeyboardButton('Programming technologies')
        itembtn3 = types.KeyboardButton('Mathematical statistics')
        itembtn4 = types.KeyboardButton('Physics')
        itembtn5 = types.KeyboardButton('Electronics/engineering')
        itembtn6 = types.KeyboardButton('Databases')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
        bot.send_message(message.chat.id, "Choose discipline:", reply_markup=markup)

    elif message.text == "/check_deadlines":
        bot.reply_to(message, "checking deadlines...")
        deadlines = check_deadlines()
        bot.send_message(message.chat.id, "Deadlines format:")
        bot.send_message(message.chat.id, "id | Discipline | Task | Deadline")
        bot.send_message(message.chat.id, "List of deadlines:")
        for deadline in deadlines:
            bot.send_message(message.chat.id, ' | '.join(map(str, deadline)))

    elif message.text == "/delete_deadlines":
        bot.reply_to(message, "write the id of the deadline")
        global deleting_process
        deleting_process = 1

    elif message.text == "/get_pdf":
        send_pic(message.chat.id)



@bot.message_handler(func=lambda message: True)
def echo_all(message):
    global discipline
    global date
    global description
    global deleting_process
    if discipline == "" and (message.text == "Applied mathematics" or message.text == "Programming technologies" or message.text == "Mathematical statistics" or message.text == "Physics" or message.text == "Electronics/engineering" or message.text == "Databases"):
        discipline = message.text
        bot.send_message(message.chat.id, "Write the deadline date in DD.MM format, for example, 12.02 (12 of February)", reply_markup=types.ReplyKeyboardRemove())
    elif (discipline != "" and date == ""):
        if len(message.text)<5 or message.text[2] != "." or not (message.text[0].isdigit()) or not (message.text[1].isdigit()) or not (message.text[3].isdigit()) or not (message.text[4].isdigit()) or int(message.text[0]+message.text[1])>31 or int(message.text[3]+message.text[4])>12:
            print ("error in datetime format", return_time())
            bot.send_message(message.chat.id, "Write the deadline date in DD.MM format, for example, 12.02")
        else:
            date = "2022-"+message.text[3]+message.text[4]+"-"+message.text[0]+message.text[1]
            print("date testing", date)
            bot.send_message(message.chat.id, "Напиши по возможности подробно, в чем заключается задание (Please in russian)")
    elif (discipline != "" and date != "" and description == ""):
        description = message.text
        add_deadline()
        bot.send_message(message.chat.id, "Deadline added successfully!")
    elif deleting_process == 1 and message.text.isdigit():
        deadlines = check_deadlines()
        delete_deadline(message.text)
        deleting_process = 0
        bot.send_message(message.chat.id, "Deadline deleted, check the deadlines list")

    else:
        bot.reply_to(message, "You are doing something wrong or programm is not working? Anyway, you can ask @kroexov")

bot.infinity_polling()
