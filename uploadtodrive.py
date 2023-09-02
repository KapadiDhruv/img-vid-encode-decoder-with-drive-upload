import os 
import json
import subprocess
import base64
import magic
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from dotenv import load_dotenv
load_dotenv()

# Define the OAuth2 credentials
CLIENT_ID = os.environ.get('DRIVE_CLIENT_ID')
CLIENT_SECRET= os.environ.get('DRIVE_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('DRIVE_REDIRECT_URI')
REFRESH_TOKEN = os.environ.get('DRIVE_REFRESH_TOKEN')
DRIVE_ACCOUNT = os.environ.get('DRIVE_ACCOUNT')

# Set up the API client
creds = Credentials.from_authorized_user_info(info={'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'refresh_token': REFRESH_TOKEN},
                                              scopes=['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)

# Define a function to recursively create folders and files
def create_folder_structure(local_path, parent_folder_id=None):
    # Create a folder on Google Drive with the same name as the local folder
    folder_name = os.path.basename(local_path)
    folder_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_folder_id:
        folder_metadata['parents'] = [parent_folder_id]
    folder = service.files().create(body=folder_metadata, fields='id, webViewLink, webContentLink').execute()
    folder_id = folder.get('id')
    folder_web_view_link = folder.get('webViewLink')
    folder_web_content_link = folder.get('webContentLink')
    print(f'Folder created: {folder_name} ({folder_id})')
    print(f'Folder webViewLink: {folder_web_view_link}')
    print(f'Folder webContentLink: {folder_web_content_link}')
    
    # Set permission to anyone with the link can view
    permission = {'type': 'anyone', 'role': 'reader', 'allowFileDiscovery': False}
    service.permissions().create(fileId=folder_id, body=permission).execute()

    # Get the contents of the local folder
    contents = os.listdir(local_path)
    folder_contents = []
    for item in contents:
        item_path = os.path.join(local_path, item)
        if os.path.isdir(item_path):
            # Recursively create subfolders
            subfolder_contents = create_folder_structure(item_path, parent_folder_id=folder_id)
            folder_contents.extend(subfolder_contents)
        else:

            ENCODED_SIZE = 0
            try:
                # Escape special characters and spaces
                escaped_path = item_path.replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace(" ", "\\ ")

                # Construct the du command with the escaped path
                du_command = f'du -hs {escaped_path}'
                ENCODED_SIZE = subprocess.check_output(du_command, shell=True, text=True)

            except subprocess.CalledProcessError:
                # If the command fails, set ENCODED_SIZE to 0
                ENCODED_SIZE = 0
            # Upload files to the current folder
            file_metadata = {'name': item, 'parents': [folder_id]}
            media = MediaFileUpload(item_path)
            file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink, webContentLink, mimeType').execute()
            file_id = file.get('id')
            file_web_view_link = file.get('webViewLink')
            file_mimetype = file.get('mimeType')
            file_contents = {'name': item, 'id': file_id, 'webViewLink': file_web_view_link, 'mimeType': file_mimetype, "size" : ENCODED_SIZE, "originalMime" : original_mimetype(item_path)}
            folder_contents.append(file_contents)
            print(f'File uploaded: {item} ({file_id})')
            print(f'File webViewLink: {file_web_view_link}')
            print(f'File mimeType: {file_mimetype}')


    # Return the folder contents
    return folder_contents

def original_mimetype(base64_file_path):
# Read the Base64-encoded data from the file
    with open(base64_file_path, 'r') as base64_file:
        base64_data = base64_file.read()

    # Decode the Base64 data to binary
    binary_data = base64.b64decode(base64_data)

    file_type_detector = magic.Magic()

    # Determine the file extension based on the content
    file_type = file_type_detector.from_buffer(binary_data)
    if ("image" in file_type):
        original_extension = '.jpg'
        return original_extension
    elif ("Video" or "MP4" or "video" in file_type):
        original_extension = '.mp4'
        return original_extension
    else:
        original_extension = None  # Unsupported format
        return original_extension

# Define the local path to the folder whose structure will be replicated
with open("sub_list.csv", "r") as f_subreddits:
    for sub in f_subreddits:
        sub = sub.strip()
        local_path = f'encoded-data/{sub}'

        # Call the function to create the folder structure
        folder_contents = create_folder_structure(local_path)

        # Write the folder contents to a JSON file
        with open(f'{sub}/file_links.json', 'w') as f:
            json.dump(folder_contents, f, indent=4)
