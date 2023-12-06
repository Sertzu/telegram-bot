
# Python program to generate WordCloud

# importing all necessery modules
#from wordcloud import WordCloud, STOPWORDS
#import matplotlib.pyplot as plt
import dill as pkl
import os


def add_message(sender, message, chat_id):
    file_path_abs = os.path.dirname(__file__)
    file_path = "TelegramBotData"
    file_name = os.path.join(file_path_abs,file_path, str(chat_id) + ".pkl")

    to_append = str(sender), str(message)
    message_dict = []
    try:
        with open(file_name, 'rb') as handle:
            message_dict = pkl.load(handle)
            message_dict.append(to_append)
    except:
        with open(file_name, 'wb') as handle:
            pkl.dump([("void", "void")], handle, protocol=pkl.HIGHEST_PROTOCOL)

    with open(file_name, 'wb') as handle:
        pkl.dump(message_dict, handle, protocol=pkl.HIGHEST_PROTOCOL)


def add_user(sender, chat_id):
    file_path_abs = os.path.dirname(__file__)
    file_path = "TelegramBotData"
    file_name = os.path.join(file_path_abs,file_path, "Users.pkl")

    to_append = [str(sender), 0]
    duplicate = False
    try:
        with open(file_name, 'rb') as handle:
            user_dict = pkl.load(handle)
            for data in user_dict:
                if data[0] == str(sender):
                    duplicate = True
            if not duplicate:
                user_dict.append(to_append)

        with open(file_name, 'wb') as handle:
            pkl.dump(user_dict, handle, protocol=pkl.HIGHEST_PROTOCOL)
    except:
        with open(file_name, 'wb') as handle:
            pkl.dump([to_append], handle, protocol=pkl.HIGHEST_PROTOCOL)
