#!/usr/bin/env python

__author__ = 'rjanardhana'

import csv
import sys
import logging
import os
import string
import time
import re

# Global logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global
DISH_CSV_FILE = "../data/Dish.csv"
MENU_STOPWORDS_FILE = "../data/MenuStopWords.txt"
CLEANED_DISH_LIST_FILE = "../data/CleanedDishList.csv"
ALPHA_WITH_SPACE_REGEX = re.compile("^[a-z\s]+$")
MIN_DISH_LEN = 3
MAX_WORDS_IN_DISH_LEN = 6


def pre_process(word):
    """
    Preprocesses the word and returns a cleaned up version by converting it to lower case and removes punctuation
    :param word: input word to preprocess
    :returns: cleaned up version of the input word
    """
    if not word:
        return ""

    # Lower case
    s = word.lower()

    # Get rid of apostrophe
    s = s.replace("'",  "")

    # Replace other punctuations with a space
    for char in string.punctuation:
        s = s.replace(char, " ")

    # Replace multiple spaces with a single space
    s = re.sub('\s+', ' ', s)

    # Strip spaces at the end
    s = s.strip()

    return s


def is_valid(dish):
    """
    :returns: true if the dish matches all the rules, else false
    """
    # min length of dish
    if len(dish) < MIN_DISH_LEN:
        return False

    # has only alphabets and space
    if not ALPHA_WITH_SPACE_REGEX.search(dish):
        return False

    word_list = dish.split(" ")

    # max words in dish check
    if len(word_list) > MAX_WORDS_IN_DISH_LEN:
        return False

    # has at least one word within that satisfies min_len check
    has_word_with_min_len = False
    for word in word_list:
        if len(word) > MIN_DISH_LEN:
            has_word_with_min_len = True
            break
    if not has_word_with_min_len:
        return False

    # cannot have more than 1 single letter word
    single_letter_word_count = 0
    for word in word_list:
        if len(word) == 1:
            single_letter_word_count += 1
            if single_letter_word_count > 1:
                return False

    # passed every check
    return True


def get_menu_stop_words():
    """
    Reads menu stop words from MENU_STOPWORDS_FILE and returns a set of it
    """
    if not os.path.exists(MENU_STOPWORDS_FILE):
        logger.error("%s does not exist, cannot proceed", MENU_STOPWORDS_FILE)
        sys.exit(1)

    menu_stop_words = set()
    with open(MENU_STOPWORDS_FILE) as fp:
        for line in fp:
            menu_stop_words.add(line.strip())
    return menu_stop_words


def generate_menu_items(menu_stop_words):
    """
    Reads dishes from DISH_CSV_FILE and writes the cleaned up dish version to CLEANED_DISH_LIST_FILE
    :return:
    """
    if not os.path.exists(DISH_CSV_FILE):
        logger.error("%s does not exist, cannot proceed", DISH_CSV_FILE)
        sys.exit(1)

    logger.info("Started processing file")
    t0 = time.clock()
    ip = open(DISH_CSV_FILE, "rb")
    csv_reader = csv.reader(ip, quoting=csv.QUOTE_MINIMAL)

    op = open(CLEANED_DISH_LIST_FILE, "wb")
    csv_writer = csv.writer(op, quoting=csv.QUOTE_MINIMAL)

    # skip header
    next(csv_reader, None)

    cleaned_dishes = set()
    count = 0
    for row in csv_reader:
        raw_dish_list = row[1].split(",")
        for raw_dish in raw_dish_list:
            preprocessed_dish = pre_process(raw_dish)
            if is_valid(preprocessed_dish) and preprocessed_dish not in menu_stop_words:
                cleaned_dishes.add(preprocessed_dish)
        count += 1
        if count % 50000 == 0:
            logger.info("Processed %d lines", count)

    cleaned_dishes = sorted(cleaned_dishes)
    logger.info("Dish count = %d", len(cleaned_dishes))

    ip.close()
    t1 = time.clock()
    logger.info("Finished processing in %f seconds", t1-t0)

    logger.info("Writing cleaned up menu items to %s", CLEANED_DISH_LIST_FILE)
    t2 = time.clock()
    for dish in cleaned_dishes:
        csv_writer.writerow([dish])
    t3 = time.clock()
    logger.info("Finished writing to disk in %f seconds", t3-t2)

if __name__ == "__main__":
    menu_stop_words = get_menu_stop_words()
    generate_menu_items(menu_stop_words)
