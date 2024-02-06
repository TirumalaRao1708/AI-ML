
from image_text_similarity import process_folder_with_images_and_text
import streamlit as st
import os
import pandas as pd
from PIL import Image

@st.cache
def load_similarity_data():
    """
    Load similarity data from a CSV file and return a DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing similarity data.
    """
    similarity_df_image = pd.read_csv(output_csv_path.replace('.csv', '_image.csv'))
    return similarity_df_image

def calculate_most_similar_images(similarity_df, selected_image):
    """
    Calculate the most similar images based on the selected image.

    Args:
        similarity_df (pd.DataFrame): DataFrame containing similarity data.
        selected_image (str): The selected image.

    Returns:
        pd.DataFrame: DataFrame with the most similar images and their similarity values.
    """
    most_similar_images = []
    for index, row in similarity_df.iterrows():
        if row['Image1'] == selected_image:
            most_similar_images.append({'Image1': row['Image1'], 'Image2': row['Image2'], 'Similarity (SSIM)': row['Image Similarity (SSIM)']})
        elif row['Image2'] == selected_image:
            most_similar_images.append({'Image1': row['Image2'], 'Image2': row['Image1'], 'Similarity (SSIM)': row['Image Similarity (SSIM)']})

    most_similar_df = pd.DataFrame(most_similar_images)
    most_similar_df = most_similar_df.sort_values(by=['Similarity (SSIM)'], ascending=False)
    return most_similar_df

def main():
    """
    Main function to create the Streamlit app for Image Similarity Analyzer.
    """
    st.title("Image Similarity Analyzer")
    #change the path of the folder as the images where they are saved
    input_folder_path = r"C:\Users\sairaj.bai\Desktop\pdf2\images_pdf\images"

    # Load similarity data using st.cache
    similarity_df_image = load_similarity_data()

    st.sidebar.header("Select Image")

    # Update selected_image based on user interaction in the sidebar
    selected_image = st.sidebar.selectbox("Select an image:", similarity_df_image['Image1'].unique())

    # Display the selected image below the sidebar
    st.subheader(f"Selected Image: {selected_image}")
    selected_image_path = os.path.join(input_folder_path, selected_image)
    try:
        selected_image_pil = Image.open(selected_image_path)
        st.sidebar.image(selected_image_pil, use_column_width=True)
    except Exception as e:
        st.sidebar.error(f"Error loading selected image: {selected_image_path}")
        st.sidebar.error(f"Error details: {e}")


    st.header("Similar Images (Descending Order)")

    all_similar_df = calculate_most_similar_images(similarity_df_image, selected_image)

    if not all_similar_df.empty:
        # Display all similar images with their similarity values in a grid with 5 images in each row
        images_per_row = 5
        total_images = len(all_similar_df)
        rows = (total_images // images_per_row) + (total_images % images_per_row > 0)

        for i in range(rows):
            columns = st.columns(images_per_row)
            for j in range(images_per_row):
                index = i * images_per_row + j
                if index < total_images:
                    row = all_similar_df.iloc[index]
                    similar_image_path = os.path.join(input_folder_path, row['Image2'])
                    try:
                        similar_image_pil = Image.open(similar_image_path).resize((150, 150))
                        columns[j].image(similar_image_pil, caption=f"{row['Image2']} - Similarity: {row['Similarity (SSIM)']:.4f}")
                    except Exception as e:
                        st.warning(f"Error loading similar image: {similar_image_path}")
                        st.warning(f"Error details: {e}")

    else:
        st.warning("No similar images found.")

if __name__ == "__main__":
    # Define the paths for output files
    output_pickle_path = 'output_all_simila.pkl'
    output_csv_path = 'output_all_similar.csv'
    #change the path of the input folder as desired 
    # Process the data and run the Streamlit app
    process_folder_with_images_and_text(r"C:\Users\sairaj.bai\Desktop\pdf2\images_pdf", output_pickle_path, output_csv_path)
    main()
