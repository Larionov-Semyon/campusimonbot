import os


toggles = {
    'exhibition': 'Выставки',
    'meeting': 'Собрания',
    'educational': 'Познавательное',
    'science': 'Наука',
    'career': 'Карьерные мероприятия',
    'networking': 'Нетворкинг',
    'forum': 'Форумы и фестивали',
}


def get_admins():
    return os.environ["ADMINS"].split()


def get_creator():
    return os.environ["CREATOR"]
