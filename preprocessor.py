import re
import pandas as pd
def preprocess(data):
    # Match pattern with AM/PM and possible narrow no-break space (Unicode \u202f)
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?\u202f?[AP]M\s-\s'

    # Split based on the pattern and get date strings
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Clean date strings
    dates = [date.strip().replace('\u202f', ' ') for date in dates]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert to datetime using 12-hour format, handling errors by setting them to NaT
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p -', errors='coerce')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Convert 'hour' column to int before formatting
    # df['hour'] = df['hour'].astype(int) #This will raise error if NaN values present
    df['hour'] = df['hour'].fillna(0).astype(int)  # Fill NaN with 0 and then convert to int

    # Time periods
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append('23-00')
        elif hour == 0:
            period.append('00-01')
        else:
            period.append(f"{hour:02d}-{(hour + 1) % 24:02d}")  # Use f-string formatting for integers
    df['period'] = period

    return df