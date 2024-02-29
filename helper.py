import matplotlib.pyplot as plt
import spacy
import emoji
import pandas as pd
from wordcloud import WordCloud
from string import punctuation
from collections import Counter
from urlextract import URLExtract

url_extractor = URLExtract()
nlp = spacy.load("en_core_web_sm")

f = open("stop_hinglish.txt", 'r')
stop_words = f.read()
f.close()


def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df["users"] == selected_user]

    # fetch no. of messages
    num_messages = df.shape[0]

    # 2. fetch no. of words
    words = []
    for message in df.message:
        words.extend(message.split())

    # fetch no. of media messages
    num_media_messages = df[df["message"] == "<Media omitted>\n"]

    # fetch no. of links shared
    urls = []
    for message in df.message:
        urls.extend(url_extractor.find_urls(message))

    return num_messages, len(words), len(num_media_messages), len(urls)


def fetch_most_busy_users(df):
    filter_df = df[df["users"] != "group notification"]

    top_5_users = filter_df["users"].value_counts().head()
    df = round((filter_df.users.value_counts() / filter_df.shape[0]) * 100, 2).reset_index().rename(
        columns={"index": "name", "count": "percent"})

    return top_5_users, df


def create_wordcloud(selected_user, df):
    if selected_user != "Overall":
        df = df[df["users"] == selected_user]

    temp = df[df["users"] != "group notification"]
    temp = temp[temp["message"] != "<Media omitted>\n"]

    # def remove_stopwords(message):
    #     words = []
    #     for word in message.lower().split():
    #         if word not in stop_words and word not in punctuation:
    #             words.append(word)
    #     return " ".join(words)
    #
    # temp["message"] = temp["message"].apply(remove_stopwords)

    cloud = WordCloud(width=500, height=500, min_font_size=10, stopwords=set(stop_words))
    df_cloud = cloud.generate(temp["message"].str.cat(sep=" "))
    return df_cloud


def most_common_words(selected_user, df):
    if selected_user != "Overall":
        df = df[df["users"] == selected_user]

    temp = df[df["users"] != "group notification"]
    temp = temp[temp["message"] != "<Media omitted>\n"]

    words = []

    # Iterate over each message in the 'message' column
    for doc in nlp.pipe(temp["message"].astype(str)):
        # Iterate over each token in the message
        for token in doc:
            # Check if the lowercase token is not a stop word and not punctuation
            if token.text.lower() not in stop_words and token.text not in punctuation + "\n\n" and token.text not in emoji.EMOJI_DATA:
                words.append(token.text.lower())  # Append the lowercase token to 'words'

    # Count occurrences of each word and create DataFrame with 20 most common words
    word_counts = Counter(words)
    common_words_df = pd.DataFrame(word_counts.most_common(20), columns=['Word', 'Count'])

    return common_words_df


def emoji_extractor(selected_user, df):
    if selected_user != "Overall":
        df = df[df["users"] == selected_user]

    emojis = []
    for message in df.message:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
    emoji_count = Counter(emojis).most_common()
    emoji_df = pd.DataFrame(emoji_count, columns=["emoji", "count"])

    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df["users"] == selected_user]

    timeline = df.groupby(["year", "month_num", "month"]).count()["message"].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline["month"][i] + "-" + str(timeline["year"][i]))

    timeline["time"] = time

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df["users"] == selected_user]

    timeline_daily = df.groupby("only_date").count()["message"].reset_index()

    return timeline_daily


def weekly_activity(selected_user, df):
    if selected_user != "Overall":
        df = df[df["users"] == selected_user]

    return df.date.dt.day_name().value_counts()


def monthly_activity(selected_user, df):
    if selected_user != "Overall":
        df = df[df["users"] == selected_user]

    return df.month.value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != "Overall":
        df = df[df["users"] == selected_user]

    return df.pivot_table(index='day_name', columns='period', values='message', fill_value=0, aggfunc='count')

