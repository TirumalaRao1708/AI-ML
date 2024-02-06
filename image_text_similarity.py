
import fitz
import os
import PyPDF2
import pandas as pd
from Levenshtein import distance
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skimage.metrics import structural_similarity as ssim
from skimage import transform
import cv2
import numpy as np
import textdistance

nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    """
    Preprocess text by converting to lowercase, removing non-alphanumeric characters,
    tokenizing, removing stopwords, and stemming.

    Parameters:
    - text (str): Input text.

    Returns:
    - str: Preprocessed text.
    """
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    preprocessed_text = " ".join(stemmed_tokens)
    return preprocessed_text

def calculate_similarity(text1, text2, method):
    """
    Calculate similarity between two texts using specified method.

    Parameters:
    - text1 (str): First text.
    - text2 (str): Second text.
    - method (str): Similarity calculation method (Levenshtein, Cosine, Jaccard, Hamming).

    Returns:
    - float: Similarity score.
    """
    if method == "Levenshtein":
        return 1 - (distance(text1, text2) / max(len(text1), len(text2)))
    elif method == "Cosine":
        vectorizer = TfidfVectorizer().fit_transform([text1, text2])
        cosine_sim = cosine_similarity(vectorizer)
        return cosine_sim[0, 1]
    elif method == "Jaccard":
        tokens1 = set(text1.split())
        tokens2 = set(text2.split())
        intersection_size = len(tokens1.intersection(tokens2))
        union_size = len(tokens1.union(tokens2))
        jaccard_similarity = intersection_size / union_size if union_size > 0 else 0
        return jaccard_similarity
    elif method == "Hamming":
        return 1 - (textdistance.hamming.normalized_similarity(text1, text2))
    else:
        raise ValueError("Invalid similarity method")
    
desired_width = 100
desired_height = 100 

def preprocess_image(image_path):
    """
    Preprocess image by converting to grayscale, applying Gaussian blur, histogram equalization,
    resizing, and normalizing pixel values.

    Parameters:
    - image_path (str): Path to the image.

    Returns:
    - numpy.ndarray: Preprocessed image.
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray, (5, 5), 0)
    equalized_img = cv2.equalizeHist(blurred_img)
    resized_img = cv2.resize(equalized_img, (desired_width, desired_height))
    normalized_img = resized_img / 255.0
    return normalized_img

def calculate_image_similarity(image_path1, image_path2, method='ssim'):
    """
    Calculate similarity between two images using specified method.

    Parameters:
    - image_path1 (str): Path to the first image.
    - image_path2 (str): Path to the second image.
    - method (str): Image similarity calculation method ('ssim' or 'mse').

    Returns:
    - float: Image similarity index.
    """
    preprocessed_img1 = preprocess_image(image_path1)
    preprocessed_img2 = preprocess_image(image_path2)

    if method == 'ssim':
        similarity_index, _ = ssim(preprocessed_img1, preprocessed_img2, full=True, data_range=preprocessed_img2.max() - preprocessed_img2.min())
    elif method == 'mse':
        mse = np.sum((preprocessed_img1 - preprocessed_img2) ** 2) / float(preprocessed_img1.size)
        similarity_index = -mse
    else:
        raise ValueError("Invalid image similarity method")

    return similarity_index

def extract_images_from_pdf(pdf_path, images_folder_path):
    """
    Extract images from a PDF and save them to a specified folder.

    Parameters:
    - pdf_path (str): Path to the PDF file.
    - images_folder_path (str): Path to the folder to save extracted images.
    """
    if not os.path.exists(images_folder_path):
        os.makedirs(images_folder_path)

    pdf_document = fitz.open(pdf_path)

    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        image_list = page.get_images(full=True)

        for img_info in image_list:
            image_index = img_info[0]
            base_image = pdf_document.extract_image(image_index)
            image_bytes = base_image["image"]

            image_path = os.path.join(images_folder_path, f"page_{page_num + 1}_img_{image_index}.png")

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

    pdf_document.close()

def process_folder_with_images_and_text(folder_path, output_pickle_path, output_csv_path):
    """
    Process PDF files with both text and images in a folder, calculate text and image similarities,
    and save results to pickle and CSV.

    Parameters:
    - folder_path (str): Path to the folder containing PDF files.
    - output_pickle_path (str): Path to save the pickle file.
    - output_csv_path (str): Path to save the CSV file.
    """
    data = []
    similarities_text = []
    similarities_image = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            images_folder_path = os.path.join(folder_path, "images")

            extract_images_from_pdf(file_path, images_folder_path)

            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                file_text = ""

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    file_text += text.lower()

                preprocessed_text = preprocess_text(file_text)
                data.append({'File Name': file_name, 'Text': file_text, 'Preprocessed Text': preprocessed_text})

    df = pd.DataFrame(data)
    df.to_pickle(output_pickle_path)

    similarity_methods_text = ["Levenshtein", "Cosine", "Jaccard", "Hamming"]
    for method_text in similarity_methods_text:
        similarity_list_text = []
        for i in range(len(df)):
            for j in range(i + 1, len(df)):
                file1_name, text1, preprocessed_text1 = df.iloc[i]['File Name'], df.iloc[i]['Text'], df.iloc[i]['Preprocessed Text']
                file2_name, text2, preprocessed_text2 = df.iloc[j]['File Name'], df.iloc[j]['Text'], df.iloc[j]['Preprocessed Text']

                similarity_normal_text = calculate_similarity(text1, text2, method_text)
                similarity_preprocessed_text = calculate_similarity(preprocessed_text1, preprocessed_text2, method_text)

                similarity_list_text.append({'File1': file1_name, 'File2': file2_name, f'Similarity ({method_text}) (Normal Text)': similarity_normal_text,
                                        f'Similarity ({method_text}) (Preprocessed Text)': similarity_preprocessed_text})

        similarity_df_text = pd.DataFrame(similarity_list_text)
        similarities_text.append(similarity_df_text)

    similarity_methods_image = ["ssim", "mse"]
    images_folder_path = os.path.join(folder_path, "images")

    for method_image in similarity_methods_image:
        similarity_list_image = []
        image_files = [f for f in os.listdir(images_folder_path) if f.endswith(".png")]

        for i in range(len(image_files)):
            for j in range(i + 1, len(image_files)):
                image1_path = os.path.join(images_folder_path, image_files[i])
                image2_path = os.path.join(images_folder_path, image_files[j])

                image_similarity = calculate_image_similarity(image1_path, image2_path, method=method_image)

                similarity_list_image.append({'Image1': image_files[i], 'Image2': image_files[j], f'Image Similarity ({method_image.upper()})': image_similarity})

        similarity_df_image = pd.DataFrame(similarity_list_image)
        similarities_image.append(similarity_df_image)

    final_similarity_df_text = pd.concat(similarities_text, axis=1)
    final_similarity_df_text.to_csv(output_csv_path, index=False)

    final_similarity_df_image = pd.concat(similarities_image, axis=1)
    final_similarity_df_image.to_csv(output_csv_path.replace('.csv', '_image.csv'), index=False)

# Example usage
#change the path of the input folder as desired 
input_folder_path = "C:\\Users\\sairaj.bai\\Desktop\\pdf2\\images_pdf"
output_pickle_path = 'output_all_simila.pkl'
output_csv_path = 'output_all_similar.csv'
process_folder_with_images_and_text(input_folder_path, output_pickle_path, output_csv_path)

