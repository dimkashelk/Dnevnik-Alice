from .const import *
from random import randrange


def get_random_phrases(type_phrases):
    return text_phrases[type_phrases][randrange(0, len(text_phrases[type_phrases]))]
