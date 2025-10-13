import re
from collections import Counter
from urlextract import URLExtract
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import emoji
import seaborn as sns
import pandas as pd
extractor = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    num_messages = df.shape[0]
    words = df["message"].apply(lambda x: len(str(x).split())).sum()
    media_msgs = df[df["message"].str.contains("<Media omitted>", na=False)].shape[0]

    # Count links
    links = []
    for msg in df["message"]:
        links.extend(extractor.find_urls(str(msg)))
    link_count = len(links)

    return num_messages, words, media_msgs, link_count

def add_link_column(df):
    df["links_count"] = df["message"].apply(lambda msg: len(extractor.find_urls(str(msg))))
    return df

def most_busy_users(df):
    """Return top 5 most active users and full counts"""
    df = df[df["user"] != "group_notification"]
    user_counts = df["user"].value_counts()
    top5 = user_counts.head(5)

    # Plot
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(top5.index, top5.values)
    ax.set_title("Top Active Users", fontsize=12)
    ax.set_xlabel("User", fontsize=10)
    ax.set_ylabel("Message Count", fontsize=10)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()

    return top5, user_counts, fig

# def create_wordcloud(selected_user, df):
#     if selected_user != "Overall":
#         df = df[df["user"] == selected_user]

#     text = " ".join(msg for msg in df["message"] if isinstance(msg, str) and msg != "<Media omitted>")
#     wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)

#     fig, ax = plt.subplots(figsize=(10, 5))
#     ax.imshow(wordcloud, interpolation='bilinear')
#     ax.axis("off")
#     plt.tight_layout(pad=0)

#     return fig

def create_wordcloud(selected_user, df):
    # Filter for selected user
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    # Load stopwords from hinglish.txt
    try:
        with open("hinglish.txt", "r", encoding="utf-8") as f:
            stopwords = set(word.strip().lower() for word in f.readlines())
    except FileNotFoundError:
        stopwords = set()
        print("⚠️ Warning: 'hinglish.txt' not found, proceeding without custom stopwords.")

    # Combine all messages
    text = " ".join(msg for msg in df["message"] if isinstance(msg, str))

    # Remove <Media omitted> and non-alphabetic characters
    text = re.sub(r"<Media omitted>", "", text)
    text = re.sub(r"http\S+", "", text)       # remove URLs
    text = re.sub(r"[^A-Za-z\s]", "", text)   # keep only letters and spaces

    # Split words and remove stopwords
    words = [word.lower() for word in text.split() if word.lower() not in stopwords and len(word) > 1]

    # Regenerate clean text
    clean_text = " ".join(words)

    # Create WordCloud
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(clean_text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    plt.tight_layout(pad=0)

    return fig


def most_common_words(selected_user, df):
    """Return a bar plot of 15 most common words."""
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    try:
        with open("hinglish.txt", "r", encoding="utf-8") as f:
            stopwords = set(word.strip().lower() for word in f.readlines())
    except FileNotFoundError:
        stopwords = set()

    text = " ".join(msg for msg in df["message"] if isinstance(msg, str))
    text = re.sub(r"<Media omitted>", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^A-Za-z\s]", "", text)

    words = [word.lower() for word in text.split() if word.lower() not in stopwords and len(word) > 1]

    common_words = Counter(words).most_common(15)

    if not common_words:
        return None

    # Bar chart
    words_list, counts = zip(*common_words)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(words_list[::-1], counts[::-1])  # reversed for top-down order
    ax.set_title("Top 15 Most Used Words", fontsize=12)
    ax.set_xlabel("Frequency", fontsize=10)
    ax.set_ylabel("Words", fontsize=10)
    plt.tight_layout()

    return fig
def emoji_analysis(selected_user, df):
    """Return a DataFrame of most used emojis."""
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    emojis = []
    for msg in df["message"]:
        if isinstance(msg, str):
            emojis.extend([c for c in msg if emoji.is_emoji(c)])

    emoji_count = Counter(emojis).most_common(10)  # top 10 emojis

    if not emoji_count:
        return None

    emoji_df = pd.DataFrame(emoji_count, columns=["Emoji", "Count"])
    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    # Group by the new "time" column
    timeline = df.groupby("time").count()["message"].reset_index()

    # Plot line chart
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(timeline["time"], timeline["message"], marker="o", color="tab:blue")
    plt.xticks(rotation=45, ha="right")
    ax.set_title("📆 Monthly Message Timeline", fontsize=14)
    ax.set_xlabel("Month-Year", fontsize=12)
    ax.set_ylabel("Total Messages", fontsize=12)
    plt.tight_layout()

    return fig, timeline

def activity_heatmap(selected_user, df):
    """
    Returns a heatmap figure showing activity by hour of day vs day of week.
    X-axis: 12 AM - 11 PM
    Y-axis: Monday-Sunday
    """
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    # Ensure hour and day_name columns exist
    if 'hour' not in df.columns or 'day_name' not in df.columns:
        df['hour'] = df['date_time'].dt.hour
        df['day_name'] = df['date_time'].dt.day_name()

    # Create human-readable hour labels
    hour_labels = [f"{h%12 if h%12 != 0 else 12} {'AM' if h < 12 else 'PM'}" for h in range(24)]

    # Order days Monday → Sunday
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Pivot table: rows = day_name, columns = hour, values = message counts
    heatmap_data = df.pivot_table(index='day_name', columns='hour', values='message', aggfunc='count').fillna(0)
    heatmap_data = heatmap_data.reindex(days_order)

    # Rename columns to human-readable labels
    heatmap_data.columns = hour_labels

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(16, 5))
    sns.heatmap(heatmap_data, cmap="YlGnBu", linewidths=0.5, ax=ax)
    ax.set_title(f"📊 Weekly Activity Heatmap - {selected_user}", fontsize=14)
    ax.set_xlabel("Time of Day", fontsize=12)
    ax.set_ylabel("Day of Week", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def activity_heatmap(selected_user, df):
    """
    Returns a heatmap figure showing activity by hour of day vs day of week.
    X-axis: 0-23 hours
    Y-axis: Monday-Sunday
    """
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    # Make sure hour and day_name columns exist
    if 'hour' not in df.columns or 'day_name' not in df.columns:
        df['hour'] = df['date_time'].dt.hour
        df['day_name'] = df['date_time'].dt.day_name()

    # Order days correctly
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Create pivot table: rows = day_name, columns = hour, values = message counts
    heatmap_data = df.pivot_table(index='day_name', columns='hour', values='message', aggfunc='count').fillna(0)

    # Reorder rows to match days_order
    heatmap_data = heatmap_data.reindex(days_order)

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(heatmap_data, cmap="YlGnBu", linewidths=0.5, ax=ax)
    ax.set_title(f"📊 Weekly Activity Heatmap - {selected_user}", fontsize=14)
    ax.set_xlabel("Hour of Day", fontsize=12)
    ax.set_ylabel("Day of Week", fontsize=12)
    plt.tight_layout()

    return fig
def messages_per_day(selected_user, df):
    """
    Returns a bar chart figure showing total messages per day of week.
    """
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    # Ensure day_name column exists
    if 'day_name' not in df.columns:
        df['day_name'] = df['date_time'].dt.day_name()

    # Order days Monday → Sunday
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Count messages per day
    day_counts = df['day_name'].value_counts().reindex(days_order).fillna(0)

    # Plot bar chart
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(day_counts.index, day_counts.values, color='tab:orange')
    ax.set_title(f"📊 Messages per Day - {selected_user}", fontsize=14)
    ax.set_xlabel("Day of Week", fontsize=12)
    ax.set_ylabel("Total Messages", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig, day_counts
