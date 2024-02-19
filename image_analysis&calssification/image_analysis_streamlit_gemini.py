import os
import textwrap
import time
from PIL import Image
import streamlit as st
from IPython.display import Markdown

import google.generativeai as genai

def to_markdown(text):
    """
    Convert the given text to Markdown format.

    Args:
        text (str): The input text to be converted.

    Returns:
        Markdown: The Markdown-formatted text.
    """
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def get_chat_history():
    """
    Retrieve the chat history from the Streamlit session state.

    Returns:
        list: The chat history.
    """
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    return st.session_state.chat_history

def generate_system_prompt():
    """
    Generate system prompts for guiding user interaction.

    Returns:
        list: A list of system prompts.
    """
    system_prompts = [
        '''You're an interactive bot that analyzes the image based on the initial question and answers the user questions based on the response for the initial question. Generate and summarize the response for the user questions only based on the response generated for the initial question.''',
        '''The image analysis response is saved in the {img_analysis}''',
        '''Remember, avoid disclosing sensitive medical information in your responses. The system focuses on general information and does not process personal health data.''',
        '''Feel free to ask about the image analysis results or any general information related to the image.''',
        '''To get detailed information, try asking questions like: "What are the key features in the image?" or "Explain the analysis results in more detail."''',
        '''If you want to explore specific aspects of the analysis, consider asking questions about particular organs or structures in the image.''',
        '''Keep in mind that the system provides general information and is not a substitute for professional medical advice. Consult with a healthcare professional for personalized guidance.'''
    ]
    return system_prompts

def main():
    """
    Main function for the Streamlit application.
    """
    global system_prompt_displayed  
    system_prompt_displayed = False  

    st.title("Generative AI Content Generator")

    genai.configure(api_key='your api key')

    img_path = st.file_uploader("Upload an image:", type=['jpg', 'png', 'jpeg'])
    vision_model = genai.GenerativeModel('gemini-pro-vision')
    text_model = genai.GenerativeModel('gemini-pro')
    chat_history = get_chat_history()
    img_analysis = None
   
    st.info("Upload an image to start the analysis. Supported formats: JPG, PNG, JPEG")

    if img_path is not None:
        img = Image.open(img_path)
        st.image(img, caption="Uploaded Image.", width=200)

        initial_question = "Please analyze this image thoroughly..."
        
        try:
            img_analysis_response = vision_model.generate_content([initial_question, img], stream=True)
            img_analysis_response.resolve()
            img_analysis = img_analysis_response.text  
            st.success("Image analysis completed. You can now ask questions about the image.")
        except Exception as e:
            st.error(f"Error during initial image analysis: {e}")
            return

    user_question = st.text_input("Ask a question:")

    if st.button("Ask"):
        if user_question:
            st.subheader(f"Question: {user_question}")
            start_time_question = time.time()

            try:
                chat_history.append(f"User: {user_question}")
                response = text_model.generate_content([user_question, img_analysis], stream=True)
                response.resolve()
                chat_history.append(f"AI: {response.text}")
                st.write(f"Response: {response.text}")
                st.markdown("---")
                end_time_question = time.time()
                question_time = end_time_question - start_time_question
                st.write(f"Time taken for question analysis: {question_time:.2f} seconds")
            except Exception as e:
                st.error(f"Error during question generation: {e}")

    st.subheader("Chat History:")
    for chat_entry in chat_history:
        st.write(chat_entry)

    global messages  
    if not system_prompt_displayed:
        system_prompts = generate_system_prompt()
        for system_prompt in system_prompts:
            messages.append({"role": "assistant", "content": system_prompt})
        system_prompt_displayed = True

if __name__ == "__main__":
    messages = []
    main()
