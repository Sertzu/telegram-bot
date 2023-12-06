
# Python program to generate WordCloud

# importing all necessery modules
#from wordcloud import WordCloud, STOPWORDS
#import matplotlib.pyplot as plt
import dill as pkl
import os
import sys



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

"""
def wordcloud_bot(name, chat_id):
    # Reads 'Youtube04-Eminem.csv' file
    file_path = "C:\\Users\\Markus\\Documents\\TelegramBotData"
    file_name = os.path.join(file_path, str(chat_id) + ".pkl")
    try:
        with open(file_name, 'rb') as handle:
            message_dict = pkl.load(handle)
    except:
        return "1"

    if name[0] == "@":
        name = name[1:]
    comment_words = ''
    stopwords = set(STOPWORDS)

    # iterate through the csv file
    for val in message_dict:
        if val[0] == name:
            # typecaste each val to string
            message = str(val[1])

            # split the value
            tokens = message.split()

            # Converts each token into lowercase
            for i in range(len(tokens)):
                tokens[i] = tokens[i].lower()

            comment_words += " ".join(tokens) + " "

    if comment_words == '':
        return "0"

    wordcloud = WordCloud(width=800, height=800,
                          background_color='black',
                          stopwords=stopwords,
                          min_font_size=10).generate(comment_words)

    # plot the WordCloud image
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.imshow(wordcloud)

    path = os.path.join(sys.path[0], "temp_wordcloud.png")
    plt.savefig(path)
    return path
"""

if __name__ == '__main__':
    # wordcloud_bot()
    pass