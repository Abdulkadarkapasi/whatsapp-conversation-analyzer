import re
import pandas as pd

# A function to map phone numbers with labels
phone_number_to_label = {}
phone_number_pattern = r'(\+\d{2} \d{5} \d{5})'


# Function to replace phone numbers to labels
def replace_phone_numbers_with_labels(text):
    global phone_number_to_label
    if re.match(phone_number_pattern, text):
        if text not in phone_number_to_label:
            phone_number_to_label[text] = f'user{len(phone_number_to_label) + 1}'
        return phone_number_to_label[text]
    return text


def preprocess(data):
    pattern = "\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s"

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({"user_message": messages, "message_date": dates})

    df["message_date"] = pd.to_datetime(df["message_date"], format="%d/%m/%Y, %H:%M - ")

    df.rename(columns={"message_date": "date"}, inplace=True)

    users = []
    messages = []

    for message in df.user_message:
        entry = re.split("([\w\W]+?):\s", message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append("group notification")
            messages.append(entry[0])

    df["users"] = users
    df["message"] = messages

    df.drop(columns=["user_message"], inplace=True)

    df["users"] = df["users"].apply(replace_phone_numbers_with_labels)

    df["year"] = df.date.dt.year
    df["month"] = df.date.dt.month_name()
    df["month_num"] = df.date.dt.month
    df["day"] = df.date.dt.day
    df["hour"] = df.date.dt.hour
    df["minute"] = df.date.dt.minute
    df["only_date"] = df.date.dt.date
    df["day_name"] = df.date.dt.day_name()

    period = []
    for hour in df[["day_name", "hour"]]["hour"]:
        if hour == 23:
            period.append(str(hour) + "-" + "00")
        elif hour == 0:
            period.append("00" + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df["period"] = period

    return df


