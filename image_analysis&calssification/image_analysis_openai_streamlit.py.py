import streamlit as st
from PIL import Image
import openai
import google.generativeai as genai
import time

st.title("Generative AI Content Generator Bot")

genai.configure(api_key='AIzaSyCga-yaYEdtxz6Dgj10yQwf5onIemUW-Fc')
openai.api_key = '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'

def gemini_pro_vision(question, image):
    """
    Generates content based on a question and an image using the Gemini Pro Vision model.

    Parameters:
        question (str): The question to generate content for.
        image (PIL.Image): The image to be used for content generation.

    Returns:
        str or None: The generated content response, or None if an error occurs.
        float or None: The time taken for content generation, or None if an error occurs.
    """
    start_time = time.time()
    genai_model = genai.GenerativeModel('gemini-pro-vision')
    try:
        response = genai_model.generate_content([question, image], stream=True)
        response.resolve()
        end_time = time.time()
        time_taken = end_time - start_time
        return response.text, time_taken
    except Exception as e:
        st.warning(f"Error generating response from Gemini Pro Vision: {e}")
        return None, None

def gpt_turbo(messages):
    """
    Generates a response based on a conversation history using the GPT-3.5 Turbo model.

    Parameters:
        messages (list): A list of dictionaries representing the conversation history,
                         with each dictionary containing the 'role' and 'content' keys.

    Returns:
        str or None: The generated response, or None if an error occurs.
        float or None: The time taken for response generation, or None if an error occurs.
    """
    start_time = time.time()
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        end_time = time.time()
        time_taken = end_time - start_time
        return response.choices[0].message['content'], time_taken
    except Exception as e:
        st.error(f"An error occurred with GPT-3.5 Turbo: {e}")
        return None, None

def main():
    """
    Main function to run the Streamlit app for generating AI-generated content based on an uploaded image and user questions.
    """
    img_path = st.file_uploader("Upload an image:", type=['jpg', 'png', 'jpeg', 'tif', 'tiff'])  # Optional image upload
    user_questions = st.text_area("Enter your questions (separate each question with a new line):", "").splitlines()

    if img_path is not None:
        st.info("Image uploaded.")
        img = Image.open(img_path)
        st.image(img, caption="Uploaded Image.", width=200)
        
        if user_questions:
            prompt_response, time_taken_gemini = gemini_pro_vision(user_questions[0], img)
            if prompt_response:
                st.write(f"Response to the prompt: {prompt_response}")
                st.write(f"Time taken for image reading with gemini-pro-vision: {time_taken_gemini:.2f} seconds")
                st.markdown("---")
                
                
                for idx, question in enumerate(user_questions[1:], start=1):
                    messages = [
                        {"role": "user", "content": prompt_response},
                        {"role": "assistant", "content": question}
                    ]
                    response, time_taken_gpt = gpt_turbo(messages)
                    if response:
                        st.write(question)
                        st.write(f"Response: {response}")
                        st.write(f"Time taken for answering question {idx + 1} with GPT-3.5 Turbo: {time_taken_gpt:.2f} seconds")
                        st.markdown("---") 
            else:
                st.warning("Failed to generate response for the first question with Gemini Pro Vision.")
        else:
            st.warning("Please enter at least one question.")
    else:
        st.warning("Please upload an image.")

if __name__ == "__main__":
    main()
