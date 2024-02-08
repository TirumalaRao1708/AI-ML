import streamlit as st
import pandas as pd
from text_similarity import process_folder
 
def main():
    """
    Streamlit app for PDF Similarity Analysis.
 
    Displays a DataFrame of PDF similarity results and allows users to select a similarity method.
 
    """
    st.title("PDF Similarity Analysis App")
 
    # Load CSV file
    csv_file_path = 'text_lanstem.csv'
    df = pd.read_csv(csv_file_path)
 
    # Display CSV data
    st.dataframe(df)
 
    # Select similarity method
    similarity_methods = df.columns[2:]
    selected_method = st.selectbox("Select Similarity Method", similarity_methods)
 
    # Filter and display results based on selected method
    st.subheader(f"Similarity Results ({selected_method})")
    st.dataframe(df[['File1', 'File2', selected_method]])
 
if __name__ == "__main__":
    # Define the paths for output files
    output_pickle_path = 'text_lanstem.pkl'
    output_csv_path = 'text_lanstem.csv'
    # Change the path of the input folder as desired 
    input_folder_path = r"C:\\Users\\sairaj.bai\\Desktop\\pdf2"
    # Process the data and run the Streamlit app
    process_folder(input_folder_path, output_pickle_path, output_csv_path)
    main()