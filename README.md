# PDF Similarity Finder

This repository contains files for finding similarity between PDF files based on text and/or images.

## File Descriptions

1. **text_similarity.py**: This file calculates the similarity between the text content of different PDF files.

2. **image_text_similarity.py**: This file calculates both text and image similarity between PDF files.

3. **streamlit.py**: This file integrates directly with `image_text_similarity.py` and displays similar images of a selected image along with their similarity values.

## Usage Instructions

Before using the files, follow these steps:

1. **Change Input Folder Directory**: In each file (`text_similarity.py`, `image_text_similarity.py`, and `streamlit.py`), locate the variable specifying the input folder directory and change it according to your PDF files' location.

2. **Install Requirements**: Run the following command in your terminal to install all the required dependencies:

    ```
    pip install -r requirements.txt
    ```

3. **Running the Files**:
   - To run `text_similarity.py`, use the command:
     ```
     python text_similarity.py
     ```
   - To run `streamlit.py`, use the command:
     ```
     streamlit run streamlit.py
     ```

## Requirements

Ensure you have Python installed on your system. You can download it from [here](https://www.python.org/downloads/).




