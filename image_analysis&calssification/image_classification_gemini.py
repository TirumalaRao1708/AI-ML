import io
from PIL import Image
import streamlit as st
import json

import google.generativeai as genai

def main():
    """
    Main function for the Generative AI Content Generator application.
    """
    st.title("Generative AI Content Generator")

    genai.configure(api_key='your api key')

    img_files = st.file_uploader("Upload images:", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])

    if img_files is not None:
        # Create a dictionary to store results
        all_results = {}

        for img_file in img_files:
            img = Image.open(io.BytesIO(img_file.read()))
            st.image(img, caption="Uploaded Image.", width=200)

            model = genai.GenerativeModel('gemini-pro-vision')

            response = generate_image_labels(model, img)

           
            image_name = img_file.name
            entire_response = response.text.strip()

            result = {"Image Name": image_name, "Response": entire_response}
            all_results[image_name] = result

        # Save results to JSON
        save_to_json(all_results)

def generate_image_labels(model, img):
    """
    Generate image labels using the specified Generative AI model.

    Args:
        model (GenerativeModel): The Generative AI model.
        img (Image): The image to be analyzed.

    Returns:
        Response: The response object from the Generative AI model.
    """
    label_prompt = 'Label this image and return the top three labels with confidence scores. Give the response just the label and its confidence score, just like "label""confidencescore"'
    response = model.generate_content([label_prompt, img], stream=True)
    response.resolve()
    return response

def save_to_json(results):
    """
    Save results to a JSON file.

    Args:
        results (dict): The dictionary containing image results.

    Returns:
        None
    """
    # Define JSON file path
    json_file_path = "image_responses_gemini.json"

    # Write results to JSON
    with open(json_file_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)

    st.success(f"Results saved to {json_file_path}")

if __name__ == "__main__":
    main()
