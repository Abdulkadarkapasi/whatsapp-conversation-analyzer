import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import plotly.express as px
import numpy as np
from wordcloud import WordCloud

import helper
import preprocessor

st.sidebar.title("Whatsapp Conversation Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique user
    user_list = df["users"].unique().tolist()
    user_list.remove("group notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis w.r.t", user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, num_words, num_media_messages, num_urls = helper.fetch_stats(selected_user, df)

        st.title("Conversations Analyzer: Unveiling Trends")
        # Add a borderline below the title
        st.markdown("<hr style='border: 2px solid blue;'>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader("Total Messages")
            st.title(num_messages)

        with col2:
            st.subheader("Total words")
            st.title(num_words)

        with col3:
            st.subheader("Media Shared")
            st.title(num_media_messages)

        with col4:
            st.subheader("Links Shared")
            st.title(num_urls)

        # Monthly Timeline
        st.header("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline["time"], timeline["message"])
        for i, value in enumerate(timeline["message"]):
            plt.text(i, value, str(value), ha='center', va='top', fontsize=5, bbox=dict(facecolor='red', alpha=0.5))
        plt.xticks(rotation="vertical", fontsize=8)
        plt.title("Month Timeline")
        plt.xlabel("Month-Year")
        plt.ylabel("Count of Messages")
        st.pyplot(fig)

        # Daily Timeline
        st.header("Daily Timeline")
        timeline_daily = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline_daily["only_date"], timeline_daily["message"], color="black")
        plt.xticks(rotation="vertical")
        plt.title("Daily Timeline")
        plt.xlabel("Daily")
        plt.ylabel("Count of Messages")
        st.pyplot(fig)

        # Activity Map
        st.header("Activity Map")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Most Busy Days")
            busy_day = helper.weekly_activity(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=busy_day.index, y=busy_day.values, fill=False, hatch="///", estimator="sum")
            ax.bar_label(ax.containers[0], fontsize=12, color="red")
            plt.title("Most Busy Days")
            plt.xlabel("WeekDays")
            plt.ylabel("Count of Messages")
            # plt.tight_layout(
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.subheader("Most Busy Months")
            busy_month = helper.monthly_activity(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=busy_month.index, y=busy_month.values, fill=False, hatch="...", estimator="sum")
            ax.bar_label(ax.containers[0], fontsize=12, color="red")
            plt.title("Most Busy Months")
            plt.xlabel("Months")
            plt.ylabel("Count of Messages")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        user_heatmap = helper.activity_heatmap(selected_user, df)
        st.header("Weekly Activity Map")
        fig, ax = plt.subplots(figsize = (15, 5))
        sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # finding the busiest users in the group
        if selected_user == "Overall":
            st.header("Most Busy Users")
            top_5_users, new_df = helper.fetch_most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Top 5 Most Busy users")
                sns.barplot(x=top_5_users.index, y=top_5_users.values, estimator="sum", color="red")
                ax.bar_label(ax.containers[0], fontsize=12, color="green")
                plt.title("Top 5 Most Busy users")
                plt.xticks(rotation="vertical")
                st.pyplot(fig)

            with col2:
                st.subheader("Most Busy users by percent (%)")
                st.dataframe(new_df, width=500)

        # word cloud
        st.header("Word Cloud")
        df_cloud = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()

        st.subheader("Frequently used Words")
        ax.imshow(df_cloud)
        plt.axis("off")
        st.pyplot(fig)

        # most common words
        common_words_df = helper.most_common_words(selected_user, df)

        st.header("Most Common Words")
        fig, ax = plt.subplots()
        sns.barplot(x=common_words_df["Word"], y=common_words_df["Count"], estimator="sum", color="green")
        ax.bar_label(ax.containers[0], fontsize=8)
        plt.title("Commonly used Words")
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

        # emoji analysis
        emoji_df = helper.emoji_extractor(selected_user, df)
        st.header("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df, width=200)

        with col2:
            # Create a bar plot using plotly
            fig = px.bar(emoji_df.head(20), x='emoji', y='count', title="Top 20 Used Emojis",
                         labels={'emoji': 'Emojis', 'count': 'Counts'})
            fig.update_layout(xaxis_tickangle=-45)  # Rotate x-axis labels for better visibility

            # Display the plot in Streamlit
            st.plotly_chart(fig, use_container_width=True)
