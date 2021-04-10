import datetime
import wordcloud
import numpy
import os
import csv
import html
import re

from wordcloud import WordCloud, STOPWORDS
from PIL import Image

common_words = ["have", "had", "the", "did", "dont", "be", "to", "of", "and", "a", "in", "that", "have", "I", "it",
                "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they",
                "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
                "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like",
                "time", "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could",
                "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
                "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want",
                "because", "any", "these", "give", "day", "most", "us", "has"]


discord_users = {
    # discord users here 
}


def process_message(wordlist):
    new_list = []
    for s in wordlist:
        s = html.unescape(s)
        s = re.sub("(<a.*?</a>)", "", s)
        s = re.sub('<span class="quote">>(.*?)</span>', '\g<1>', s)
        s = re.sub('<br>',"", s)
        s = re.sub('\'', '', s)
        s = re.sub('<(.*?)>?(.*?)</(.*?)','\g<2>', s)
        s = re.sub('https?\S+', "", s)
        s = re.sub('[^\w\s]','', s)
        new_list.append(s)
    return new_list


def get_words(username, mask_image_name):
    # discord user
    user = username
    user_id = discord_users[user]
    user_csv_data = "user_csv_data.csv"
    user_csv_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), user_csv_data)
    minlen = 2
    discord_word_list = []
    with open(user_csv_data_path, 'r', encoding="utf-8") as fc:
        csv_reader = csv.reader(fc, delimiter=',')
        for row in csv_reader:
            # fetch the user id
            if row:
                if row[0] == str(user_id):
                    for word in process_message(row[1].split()):
                        if len(word) > minlen and word not in common_words:
                            discord_word_list.append(word)

    # generates our wordcloud
    generate_wordcloud(discord_word_list, username, mask_image_name)


def generate_wordcloud(word_list, username, mask_image_name):

    mask_name = mask_image_name
    mask_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wordclouds_masks", mask_name)
    mask = numpy.array(Image.open(mask_image_path))

    # wordcloud
    wc = WordCloud(
        background_color="black",
        mask=mask,
        max_words=1000,
        stopwords=STOPWORDS
    )

    # generate our wordcloud and store the result to a file
    ext = ".png"
    wc.generate(' '.join(word_list))
    image_name = "{0}_{1}{2}".format(username, str(datetime.datetime.now().strftime("%H-%M-%S")), ext)
    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wordclouds_images", image_name)
    wc.to_file(res_path)


def main():
    get_words("", "")


if __name__ == '__main__':
    main()
