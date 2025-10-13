import re
import pandas as pd

def preprocess(data):
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:[\u202f\s]?[APap][Mm])?)\s-\s'
    split_data = re.split(pattern, data)
    dates = split_data[1::2]
    messages = split_data[2::2]
    dates = re.findall(pattern, data)
    df = pd.DataFrame({'date_time': dates, 'user_message': messages})
    users = []
    messages_cleaned = []

    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)
        if len(entry) > 2:
            users.append(entry[1])
            messages_cleaned.append(entry[2])
        else:
            users.append('group_notification')
            messages_cleaned.append(entry[0])

    df['user'] = users
    df['message'] = messages_cleaned
    df.drop(columns=['user_message'], inplace=True)
    df['date_time'] = pd.to_datetime(df['date_time'], format='%m/%d/%y, %I:%M\u202f%p', errors='coerce')

# Extract parts
    df['year'] = df['date_time'].dt.year
    df['month_name'] = df['date_time'].dt.month_name()
    df['day'] = df['date_time'].dt.day
    df['hour'] = df['date_time'].dt.hour
    df['minute'] = df['date_time'].dt.minute
    df['day_name'] = df['date_time'].dt.day_name()
    df['time'] = df['month_name'] + "-" + df['year'].astype(str)
    return df
    
