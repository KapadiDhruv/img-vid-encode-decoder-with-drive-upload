import base64
import os
import magic

# Define the source directory containing your Base64-encoded files
source_directory = 'encoded-data'

# Define the destination directory to store the decoded files
output_directory = 'decoded-data'

# Create a magic object to identify file types
file_type_detector = magic.Magic()

# Recursively iterate through the source directory
for root, subdirs, files in os.walk(source_directory):
    for base64_filename in files:
        # Construct the full path to the Base64-encoded file
        base64_file_path = os.path.join(root, base64_filename)

        # Get the relative path from the source directory
        relative_path = os.path.relpath(base64_file_path, source_directory)

        # Define the corresponding output directory and ensure it exists
        output_subdirectory = os.path.join(output_directory, os.path.dirname(relative_path))
        os.makedirs(output_subdirectory, exist_ok=True)

        # Read the Base64-encoded data from the file
        with open(base64_file_path, 'r') as base64_file:
            base64_data = base64_file.read()

        # Decode the Base64 data to binary
        binary_data = base64.b64decode(base64_data)

        # Determine the file extension based on the content
        file_type = file_type_detector.from_buffer(binary_data)
        if ("image" in file_type):
            original_extension = '.jpg'
        elif ("Video" or "MP4" in file_type):
            original_extension = '.mp4'
        else:
            original_extension = None  # Unsupported format

        # Define the path for the output file with the original file extension
        if original_extension:
            output_file_path = os.path.join(output_subdirectory, os.path.splitext(base64_filename)[0] + original_extension)

            # Write the binary data to the output file
            with open(output_file_path, 'wb') as output_file:
                output_file.write(binary_data)

            print(f"Decoded file saved as {output_file_path}")
        else:
            print(f"Skipping {base64_filename}: Unsupported file format")

print("Decoding completed.")
