import os
import tempfile
import streamlit as st
from streamlit_chat import message
from youtubequery import YoutubeQuery
from googleapiclient.discovery import build

st.set_page_config(page_title="Chat Youtube")

def display_messages():
 st.subheader("Chat")
 for i, (msg, is_user) in enumerate(st.session_state["messages"]):
    message(msg, is_user=is_user, key=str(i))
 st.session_state["thinking_spinner"] = st.empty()

import base64

import base64

def search_youtube(api_key, query):
 youtube = build('youtube', 'v3', developerKey=api_key)
 search_response = youtube.search().list(
 q=query,
 part='snippet',
 maxResults=5,
 type='video'
 ).execute()

 return [(item['snippet']['title'], f"https://www.youtube.com/watch?v={item['id']['videoId']}", item['snippet']['thumbnails']['default']['url']) 
     for item in search_response.get('items', [])]




def process_input():
 if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
    user_text = st.session_state["user_input"].strip()
    with st.session_state["thinking_spinner"], st.spinner(f"Waiting"):
        query_text = st.session_state["youtubequery"].ask(user_text)

    st.session_state["messages"].append((user_text, True))
    st.session_state["messages"].append((query_text, False))
    
def ingest_input():
 if st.session_state["selected_video"] and len(st.session_state["selected_video"].strip()) > 0:
    url = st.session_state["selected_video"].strip()
    with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
        ingest_text = st.session_state["youtubequery"].ingest(url)    

def is_openai_api_key_set() -> bool:
 return len(st.session_state["OPENAI_API_KEY"]) > 0

def main():
 if len(st.session_state) == 0:
   st.session_state["messages"] = []
   st.session_state["selected_video"] = None
   st.session_state["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
   if is_openai_api_key_set():
       st.session_state["youtubequery"] = YoutubeQuery(st.session_state["OPENAI_API_KEY"])
   else:
       st.session_state["youtubequery"] = None

 st.header("Youtube Chat")

 youtube_api_key = st.text_input("YouTube API Key", key="youtube_api_key", type="password")

 if st.text_input("OpenAI API Key", value=st.session_state["OPENAI_API_KEY"], key="input_OPENAI_API_KEY", type="password"):
   if (
       len(st.session_state["input_OPENAI_API_KEY"]) > 0
       and st.session_state["input_OPENAI_API_KEY"] != st.session_state["OPENAI_API_KEY"]
   ):
       st.session_state["OPENAI_API_KEY"] = st.session_state["input_OPENAI_API_KEY"]
       st.session_state["messages"] = []
       st.session_state["user_input"] = ""
       st.session_state["youtubequery"] = YoutubeQuery(st.session_state["OPENAI_API_KEY"])

 st.subheader("Search for YouTube Videos")
 query = st.text_input("Search for YouTube Videos", key="search_query")
 if query:
   video_recommendations = search_youtube(youtube_api_key, query)
   for title, url, thumbnail_url in video_recommendations:
       if st.button(title):
            st.image(thumbnail_url, width=100) # Display the thumbnail
            st.session_state["selected_video"] = url
            ingest_input()

 display_messages()
 st.text_input("Message", key="user_input", disabled=not is_openai_api_key_set(), on_change=process_input)

 st.divider()


if __name__ == "__main__":
 main()
