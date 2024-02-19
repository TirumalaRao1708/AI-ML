# G-Drive and Dropbox Integertaion With python

 Cloud Storage File Downloader

This Streamlit app allows you to download files from Google Drive and Dropbox.

## Features

- **Google Drive Downloader:**
  - Authenticate with Google Drive using OAuth.
  - Download files from a specified folder by providing the folder link.
  - Specify the destination path and folder name for downloaded files.

- **Dropbox Downloader:**
  - Authenticate with Dropbox using an access token.
  - Download files from a specified Dropbox folder.
  - Display total file count, start downloads, and validate downloads.



## Usage Instructions

Before using the files, follow these steps:

1. **Obtain the required credentials like access token and client secret**:
How to Obtain Access Tokens
Dropbox:

Go to Dropbox App Console.
Create a new app or use an existing one.
Obtain the access token and enter it in the app.
Google Drive:

Go to Google Cloud Console.
Create a new project.
Create OAuth client ID and obtain the client ID and secret.
Use them in the Google Drive downloader.

2. **Install Requirements**: Run the following command in your terminal to install all the required dependencies:

    ```
    pip install -r requirements.txt
    ```

3. **Running the Files**:
   - To run `cloud_streamlit.py`, use the command:
     ```
     streamlit run cloud_streamlit.py
     ```

## Requirements

Ensure you have Python installed on your system. You can download it from [here](https://www.python.org/downloads/).



