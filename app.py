import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import json
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
def get_transcript(youtube_url):
    video_code=youtube_url.split("=")[1]
    transcript=YouTubeTranscriptApi.get_transcript(video_code)
    transcript_text=""
    for i in transcript:
        transcript_text+=" "+i["text"]
    return transcript_text

def get_questions():
    prompt_temlplate="""Text: {text_content}
                      You are an expert in generating MCQ type quiz on the basis of provided content.
                      Given the above text, create a quiz of 10 multiple choice questions.
                      Make sure the questions are not repeated and check all the questions to be conforming the  given text as well
                      Make sure to format your response like the following JSON format in answer given below
                       [
                       {{ "mcq" :"multiple choice question1",
                         "options"  :{{
                                      "a":"option 1",
                                      "b":"option 2",
                                      "c":"option 3",
                                      "d":"option 4"}},
                         "answer"   : "correct choice option"}},
                       {{"mcq" :"multiple choice question2",
                         "options"  :{{
                                      "a":"option 1",
                                      "b":"option 2",
                                      "c":"option 3",
                                      "d":"option 4"}},
                         "answer"   : "correct choice option"}},
                       .
                       .
                       .
                       {{ "mcq" :"multiple choice question10",
                         "options"  :{{
                                      "a":"option 1",
                                      "b":"option 2",
                                      "c":"option 3",
                                      "d":"option 4"}},
                         "answer"   : "correct choice option" }}]"""
    llm= ChatGoogleGenerativeAI(model="gemini-pro",google_api_key=os.getenv("GOOGLE_API_KEY"))
    prompt=PromptTemplate(template=prompt_temlplate,input_variables=["text_content"])
    chain=LLMChain(llm=llm,prompt=prompt,verbose=True)
    return chain

def restart_quiz():
    session_state.mcqs = False
    session_state.quize_gen = False

st.set_page_config(page_title="Master quiz",page_icon=":pencil:")
st.title("Quiz Generator App")
youtube=st.text_input("Enter the URL....")
if youtube:
    video_id=youtube.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg")
session_state=st.session_state
if 'quize_gen' not in session_state:
    session_state.quize_gen= False
if 'mcqs' not in session_state:
    session_state.mcqs= False
if not session_state.quize_gen:
    session_state.quize_gen= st.button("Generate quiz")
if session_state.quize_gen:
    if youtube is not None:
        text=get_transcript(youtube)
        if text:
            chain=get_questions()
            if not session_state.mcqs:
                session_state.mcqs =chain.run({"text_content":text})
            js=session_state.mcqs
            questions= json.loads(js)
            selected_options = []
            correct_options = []
            for ques in questions:
                choices = list(ques["options"].values())
                selected_option = st.radio(ques["mcq"], choices, index=None)
                selected_options.append(selected_option)
                correct_options.append(ques["options"][ques["answer"]])
            submit1=st.button("Submit")
            if submit1:
                marks=0
                st.header("Quiz Result:")
                for i,quest in enumerate(questions):
                    selected=selected_options[i]
                    correct=correct_options[i]
                    q=quest["mcq"]
                    st.write(f"**{i+1}.question:**")
                    st.write(q)
                    st.write("**your answer:**")
                    if selected==correct:
                       st.success(selected)
                    else:
                        st.error(selected)
                        st.write("**correct answer:**")
                        st.write(correct)
                    st.markdown("""_____""")
                    if selected==correct:
                        marks+=1
                st.info(f"#### You have scored: {marks}/10 marks")
                if st.button("Restart",on_click= restart_quiz):
                    pass
    else:
        st.write("Please provide the URL")


