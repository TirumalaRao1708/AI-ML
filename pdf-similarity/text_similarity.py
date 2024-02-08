
import os
import re
import nltk
import PyPDF2
import pandas as pd
import textdistance
from Levenshtein import distance
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
nltk.download('stopwords')

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

def process_folder(folder_path, output_pickle_path, output_csv_path):
    """
    Process PDF files in a folder, calculate similarities, and save results to pickle and CSV.

    Parameters:
    - folder_path (str): Path to the folder containing PDF files.
    - output_pickle_path (str): Path to save the pickle file.
    - output_csv_path (str): Path to save the CSV file.
    """
    data = []
    similarities = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)

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

    similarity_methods = ["Levenshtein", "Cosine", "Jaccard", "Hamming"]
    for method in similarity_methods:
        similarity_list = []
        for i in range(len(df)):
            for j in range(i + 1, len(df)):
                file1_name, text1, preprocessed_text1 = df.iloc[i]['File Name'], df.iloc[i]['Text'], df.iloc[i]['Preprocessed Text']
                file2_name, text2, preprocessed_text2 = df.iloc[j]['File Name'], df.iloc[j]['Text'], df.iloc[j]['Preprocessed Text']

                similarity_normal_text = calculate_similarity(text1, text2, method)
                similarity_preprocessed_text = calculate_similarity(preprocessed_text1, preprocessed_text2, method)

                similarity_list.append({'File1': file1_name, 'File2': file2_name,
                                        f'Similarity ({method}) (Normal Text)': similarity_normal_text,
                                        f'Similarity ({method}) (Preprocessed Text)': similarity_preprocessed_text})

        similarity_df_method = pd.DataFrame(similarity_list)
        similarities.append(similarity_df_method)

    final_similarity_df = pd.concat(similarities, axis=1)
    final_similarity_df.to_csv(output_csv_path, index=False)

# Example usage
#change the path of the input folder as desired 
input_folder_path = "C:\\Users\\sairaj.bai\\Desktop\\pdf2"
output_pickle_path = 'output_all_similarities_text.pkl'
output_csv_path = 'output_all_similarities_text.csv'
process_folder(input_folder_path, output_pickle_path, output_csv_path)
