# app.py
import streamlit as st
import pandas as pd
from preprocessor import preprocess
from helper import fetch_stats, add_link_column, most_busy_users, create_wordcloud, most_common_words, emoji_analysis, monthly_timeline, activity_heatmap, messages_per_day  
import matplotlib.pyplot as plt



st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.title("💬 WhatsApp Chat DataFrame Viewer")

# Sidebar section
st.sidebar.header("📂 Upload & Filter")

uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Chat (.txt)", type=["txt"])

if "analyze_clicked" not in st.session_state:
    st.session_state.analyze_clicked = False

if uploaded_file is not None:
    raw_bytes = uploaded_file.read()
    try:
        text_data = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        st.error("Error decoding file — please ensure it's UTF-8 encoded.")
        st.stop()

    with st.spinner("Processing chat..."):
        df = preprocess(text_data)

    # Remove group notifications
    df = df[df["user"] != "group_notification"].reset_index(drop=True)

    # Add link count column
    df = add_link_column(df)

    unique_users = sorted(df["user"].unique().tolist())
    user_options = ["Overall"] + unique_users

    selected_user = st.sidebar.selectbox("👤 Select a user", user_options)

    if st.sidebar.button("🔍 Analyze"):
        st.session_state.analyze_clicked = True

    if st.session_state.analyze_clicked:
        num_messages, words, media_msgs, link_count = fetch_stats(selected_user, df)

        st.success(f"✅ Chat analyzed for: **{selected_user}**")

        # Display Statistics
        st.subheader("📊 Chat Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Messages", num_messages)
        with col2:
            st.metric("Total Words", words)
        with col3:
            st.metric("Media Shared", media_msgs)
        with col4:
            st.metric("Links Shared", link_count)

        # Monthly Timeline
        st.subheader("📅 Monthly Activity Timeline")
        fig_timeline, timeline_df = monthly_timeline(selected_user, df)
        st.pyplot(fig_timeline)

        with st.expander("View Timeline Data"):
            st.dataframe(timeline_df[["time", "message"]], use_container_width=True)

        # Most Busy Users
        if selected_user == "Overall":
            st.subheader("👥 Most Busy Users")
            top5, user_counts, fig = most_busy_users(df)
            st.pyplot(fig)
            st.dataframe(user_counts, use_container_width=True)
        

        st.markdown("---")

        # #wordcloud
      
        st.subheader("🌐 Word Cloud")
        fig_wc = create_wordcloud(selected_user, df)
        st.pyplot(fig_wc)

        # Most Common Words
        st.subheader("📈 Most Common Words")
        fig_words = most_common_words(selected_user, df)
        if fig_words:
            st.pyplot(fig_words)
        else:
            st.info("No sufficient text data to display word frequencies.")

        st.markdown("---")

        # Emoji Analysis
        st.subheader("😀 Most Used Emojis")
        emoji_df = emoji_analysis(selected_user, df)

        if emoji_df is not None and not emoji_df.empty:
            # Style the emojis for bigger font
            styled_df = emoji_df.style.set_properties(**{
                "font-size": "25px",  # make emojis larger
                "text-align": "center"
            })
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No emojis found for the selected user.")
            st.markdown("---")

        # Activity Heatmap
        st.subheader("🔥 Weekly Activity Heatmap")
        fig_heatmap = activity_heatmap(selected_user, df)
        st.pyplot(fig_heatmap)

        # Messages per Day Bar Chart
        st.subheader("📈 Messages by Day of Week")
        fig_day, day_counts = messages_per_day(selected_user, df)
        st.pyplot(fig_day)

        with st.expander("View Message Counts by Day"):
            st.dataframe(day_counts.rename("Total Messages").reset_index().rename(columns={"index": "Day"}))



        # Display DataFrame
        if selected_user == "Overall":
            st.dataframe(df, use_container_width=True)
        else:
            st.dataframe(df[df["user"] == selected_user], use_container_width=True)
    else:
        st.info("Click **Analyze** to view message statistics.")
else:
    st.info("Please upload a WhatsApp chat file to begin.")
