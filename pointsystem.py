import os
import dill as pkl
from random import random


class Point_System:
    def __init__(self):
        file_path_abs = os.path.dirname(__file__)
        file_path = "TelegramBotData"
        self.file_name = os.path.join(file_path_abs,file_path, "Users.pkl")
        with open(self.file_name, 'rb') as handle:
            user_dict = pkl.load(handle)
        self.all_data = user_dict

    def save(self):
        with open(self.file_name, 'wb') as handle:
            pkl.dump(self.all_data, handle, protocol=pkl.HIGHEST_PROTOCOL)

    def update(self, target, number):
        for data in self.all_data:
            if data[0] == target or target == "ALL":
                data[1] += number
        self.save()

    def set(self, target, number):
        for data in self.all_data:
            if data[0] == target or target == "ALL":
                data[1] = number
        self.save()

    def get(self, target):
        for data in self.all_data:
            if data[0] == target:
                return data[1]


def wintercash(money, games, username):
    order = ""
    playcount = 1
    try:
        if int(games) > 100:
            return [money, "100 IST MAXIMUM"]
        while playcount <= int(games):
            if random() < 0.5:
                money -= 2 / 5 * money
                order = order + "L "
            else:
                if username == "Lienerbruenn":
                    money += 8 / 10 * money
                else:
                    money += 1 / 2 * money
                order = order + "W "
            playcount += 1
        return [money, order]
    except:
        return [money, "NICHT GÜLTIGE SPIELANZAHL"]


def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])


if __name__ == "__main__":
    """
    PS = Point_System()
    PS.set("ALL", 100)
    print(PS.get("MarkMuruk"))
    PS.save()
    """
    PS = Point_System()
    PS.set("ALL", 1000)



