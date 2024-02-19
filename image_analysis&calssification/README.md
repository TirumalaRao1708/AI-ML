# Image analysis and Classification Bot

This Folder contains files for Image analysis and answers the questions of user using the Gemini Pro and OpenAI and Image classification using the Gemini Pro Vision.

## File Descriptions

1. **image_analysis_gemini_streamlit.py**: This file is a streamlit app takes the image and does the analsysis using Gemini Pro Vision and user can ask any question regarding the image it answers using the Gemini Pro.

2. **image_classification_gemini_streamlit.py**: This file is a streamlit app takes multiple images at once and label them and saves it into the Json.

3. **image_analysis_openai_streamlit.py**: This file is a streamlit app takes the image and does the analsysis using Gemini Pro Vision and user can ask any question regarding the image it answers using the OpenAI.


## Usage Instructions

Before using the files, follow these steps:

1. **Change the api keys for the GEmini and OpenAI**: Before runing please change the api keys with the current api key for the Gemini and OpenAI.

2. **Install Requirements**: Run the following command in your terminal to install all the required dependencies:

    ```
    pip install -r requirements.txt
    ```

3. **Running the Files**:
   - To run `image_analysis_gemini_streamlit.py`, use the command:
     ```
     streamlit run image_analysis_gemini_streamlit.py
     ```
   - To run `image_classification_gemini_streamlit.py`, use the command:
     ```
     streamlit run image_classification_gemini_streamlit.py
     ```
   - To run `image_analysis_openai_streamlit.py`, use the command:
     ```
     streamlit run image_analysis_openai_streamlit.py
     ```

## Requirements

Ensure you have Python installed on your system. You can download it from [here](https://www.python.org/downloads/).



