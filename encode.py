import base64
import os
import shutil
from tqdm import tqdm  # Import tqdm

# Define the source directory containing your video files
source_directory = 'original-data'

# Define the destination directory to store Base64-encoded files
output_directory = 'encoded-data'

# Recursively iterate through the source directory
for root, subdirs, files in os.walk(source_directory):
    for video_filename in tqdm(files, desc=os.path.basename(root)):
        # Construct the full path to the video file
        video_path = os.path.join(root, video_filename)

        # Get the relative path from the source directory
        relative_path = os.path.relpath(video_path, source_directory)

        # Define the corresponding output directory and ensure it exists
        output_subdirectory = os.path.join(output_directory, os.path.dirname(relative_path))
        os.makedirs(output_subdirectory, exist_ok=True)

        # Read the video file in binary mode
        with open(video_path, 'rb') as video_file:
            # Read the binary data
            video_binary = video_file.read()

        # Encode the binary data as Base64
        video_base64 = base64.b64encode(video_binary).decode('utf-8')

        # Define the path for the output Base64 file
        output_base64_path = os.path.join(output_subdirectory, os.path.splitext(video_filename)[0] + '_base64.txt')

        # Write the Base64-encoded video to a file
        with open(output_base64_path, 'w') as output_file:
            output_file.write(video_base64)

        # tqdm.write(f"Base64-encoded video saved to {output_base64_path}")

print("Conversion completed.")
