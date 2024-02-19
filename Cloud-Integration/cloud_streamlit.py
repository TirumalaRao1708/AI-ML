import os
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import dropbox


script_directory = os.path.dirname(os.path.realpath(__file__))
client_secrets_path = os.path.join(script_directory, 'client_secrets.json')


def authenticate():
    """Authenticate with Google Drive and return the drive instance."""
    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['client_config_file'] = client_secrets_path
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive


def extract_folder_id(folder_link):
    """Extract folder ID from the Google Drive folder link."""
    try:
        folder_id = folder_link.split('/')[-1].split('?')[0]
        return folder_id
    except Exception as e:
        st.error(f"Error extracting folder ID: {e}")
        return None


def download_folder(folder_link, destination_path, folder_name):
    """Download files from a Google Drive folder."""
    try:
        drive = authenticate()

        
        folder_id = extract_folder_id(folder_link)

        if folder_id:
            st.write(f"Folder ID: {folder_id}")

            
            query = f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'"

            file_list = drive.ListFile({'q': query}).GetList()

            
            if file_list:
                
                local_folder_path = os.path.join(destination_path, folder_name)
                os.makedirs(local_folder_path, exist_ok=True)

                for drive_file in file_list:
                    original_file_name = drive_file['title']
                    file_path = os.path.join(local_folder_path, original_file_name)
                    drive_file.GetContentFile(file_path)

                st.success(f"{folder_name} is downloaded at {local_folder_path}")
            else:
                st.error("User is not authorized to download.")
        else:
            st.error("Error: Unable to extract folder ID.")
    except Exception as e:
        st.error(f"Error: {e}")


def download_from_dropbox():
    """Download files from Dropbox."""
    global currentcount
    for entry in dbx.files_list_folder(dropbox_download_dir, include_non_downloadable_files=False).entries:
        if "." in entry.name: 
            currentcount += 1
            newpath = os.path.join(local_download_path, dropbox_download_dir)
            os.makedirs(newpath, exist_ok=True)
            downloadto = os.path.abspath(os.path.join(local_download_path, dropbox_download_dir, entry.name))
            filedir = os.path.join(dropbox_download_dir, entry.name)
            try:
                dbx.files_download_to_file(downloadto, filedir)
                st.write(f"Downloaded {entry.name}! \nCount: {currentcount}/{totalcount}")
            except dropbox.exceptions.ApiError:
                st.write(f"Failed to download file: {entry.name}\nReason: API Error")
        else:
            try:
                st.download(os.path.join(dropbox_download_dir, entry.name))
            except dropbox.exceptions.ApiError:
                currentcount += 1
                newpath = os.path.join(local_download_path, dropbox_download_dir)
                os.makedirs(newpath, exist_ok=True)
                downloadto = os.path.abspath(os.path.join(local_download_path, dropbox_download_dir, entry.name))
                filedir = os.path.join(dropbox_download_dir, entry.name)
                try:
                    dbx.files_download_to_file(downloadto, filedir)
                    st.write(f"Downloaded {entry.name}! \nCount: {currentcount}/{totalcount}")
                except dropbox.exceptions.ApiError:
                    st.write(f"Failed to download file: {entry.name}\nReason: API Error")


def get_file_count(path):
    """Recursively get the total file count from Dropbox."""
    count = 0
    for entry in dbx.files_list_folder(path, include_non_downloadable_files=False).entries:
        if "." in entry.name:  
            count += 1
        else:
            try:
                count += get_file_count(os.path.join(path, entry.name))
            except dropbox.exceptions.ApiError:
                count += 1
    return count


def validate_dropbox():
    """Validate downloaded files from Dropbox."""
    skipped = []
    for entry in dbx.files_list_folder(dropbox_download_dir, include_non_downloadable_files=False).entries:
        if "." in entry.name: 
            if not os.path.exists(os.path.abspath(os.path.join(local_download_path, dropbox_download_dir, entry.name))):
                skipped.append(os.path.join(dropbox_download_dir, entry.name))
        else:
            try:
                skipped.extend(validate_dropbox(os.path.join(dropbox_download_dir, entry.name)))
            except dropbox.exceptions.ApiError:
                if not os.path.exists(os.path.abspath(os.path.join(local_download_path, dropbox_download_dir, entry.name))):
                    skipped.append(os.path.join(dropbox_download_dir, entry.name))
    return skipped

st.title("Cloud Storage File Downloader")

selected_page = st.sidebar.selectbox("Select Page", ["Home", "Help"])

# Home page
if selected_page == "Home":
    
    selected_service = st.sidebar.selectbox("Select Cloud Storage Service", ["Google Drive", "Dropbox"])

    
    if selected_service == "Google Drive":
        st.title("Google Drive File Downloader")

        
        folder_link = st.text_input("Enter Google Drive Folder Link:")
        destination_path = st.text_input("Enter Destination Path:", key='destination_path', value=os.getcwd(), type='default')
        folder_name = st.text_input("Enter Folder Name:")

        
        if st.button("Download Folder"):
            if folder_link and destination_path and folder_name:
                download_folder(folder_link, destination_path, folder_name)

    
    elif selected_service == "Dropbox":
        st.title("Dropbox Downloader")

        
        dropbox_token = st.text_input("Enter your Dropbox access token:", help="Follow the steps in the Help page to obtain your Dropbox access token.")
        if not dropbox_token:
            st.warning("Please enter your Dropbox access token.")
            st.stop()

        
        dropbox_download_dir = st.text_input("Enter your Dropbox download directory path:")
        if not dropbox_download_dir:
            st.warning("Please enter your Dropbox download directory path.")
            st.stop()

        
        settings = {
            "access-token": dropbox_token,
            "local-download-path": "./downloads/",  
            "dropbox-download-dir": dropbox_download_dir
        }

        local_download_path = settings["local-download-path"]
        dbx = dropbox.Dropbox(settings["access-token"])
        st.write("Logged in.")

        
        st.write("Getting total file count...")
        totalcount = get_file_count(dropbox_download_dir)
        st.write("Done. Total files: ", totalcount)

        
        st.write("Starting downloads...")
        currentcount = 0
        download_from_dropbox()
        st.write("Finished downloading!")

        
        st.write("Validating downloads...")
        failed = validate_dropbox()
        if len(failed) != 0:
            with open("failed.txt", "w+") as f:
                f.write('\n'.join(failed))
            st.write(f"Done!\n{len(failed)} file(s) failed to download.")
            st.write("View failed.txt for a list of these files.")
        else:
            st.write("Done!\nAll files successfully downloaded.")


elif selected_page == "Help":
    st.title("Help - Cloud Storage File Downloader")
    st.markdown("""
    ## Welcome to the Cloud Storage File Downloader Help Page

    This Streamlit app allows you to download files from Google Drive and Dropbox.

    ### How to Obtain Dropbox Access Token:
    1. Go to [https://www.dropbox.com/developers/apps](https://www.dropbox.com/developers/apps).
    2. Click on "Create App" or select an existing app.
    3. Choose the type of access you need (Full dropbox or App folder).
    4. Configure the app settings.
    5. Once the app is created, scroll down to the "OAuth 2" section.
    6. Click on the "Generate" button next to the "OAuth 2 access token" to get your access token.
    7. Copy the generated access token and paste it into the "Enter your Dropbox access token" field on the Home page.

    ### How to Obtain Google Drive Client ID and Client Secret:
    1. Go to [https://console.developers.google.com/](https://console.developers.google.com/).
    2. Create a new project or select an existing project.
    3. In the sidebar, navigate to "Credentials."
    4. Click on "Create Credentials" and choose "OAuth client ID."
    5. Select the application type as "Desktop app."
    6. Enter a name for your OAuth client ID.
    7. Click on "Create."
    8. In the credentials tab, find your client ID and client secret.
    9. Copy the client ID and client secret and use them in the Google Drive downloader.

    If you encounter any issues or have questions, feel free to reach out for assistance.
    """)
