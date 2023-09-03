import os
import shutil

# Function to calculate the size of a folder and its contents recursively
def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

# Source folder path (change this to your source folder)
source_folder = "encoded-data"

# Size of each batch in bytes (1 GB)
batch_size = 1024 * 1024 * 1024

# Create a root folder for batches
root_folder = "test"  # Change this to your desired root folder
os.makedirs(root_folder, exist_ok=True)

total_source_size = get_folder_size(source_folder)
num_batches = total_source_size // batch_size + 1  # Number of batches needed

# Set to keep track of copied files
copied_files = set()

# Create and populate batch folders
for i in range(num_batches):
    batch_folder = os.path.join(root_folder, f"batch_{i + 1}")
    
    # Check if the batch size is 0, and skip creating the folder
    if os.path.exists(batch_folder):
        if get_folder_size(batch_folder) == 0:
            print(f"Skipping batch {i + 1} as its size would be 0.")
            continue
    
    os.makedirs(batch_folder, exist_ok=True)

    batch_size_so_far = 0
    files_copied = 0

    for dirpath, dirnames, filenames in os.walk(source_folder):
        if batch_size_so_far >= batch_size:
            break

        for filename in filenames:
            source_file = os.path.join(dirpath, filename)
            target_file = os.path.join(batch_folder, os.path.relpath(source_file, source_folder))
            file_size = os.path.getsize(source_file)

            if batch_size_so_far + file_size <= batch_size and source_file not in copied_files:
                # Create the destination directory if it doesn't exist
                os.makedirs(os.path.dirname(target_file), exist_ok=True)

                # Copy the file to the batch folder
                shutil.copy2(source_file, target_file)
                batch_size_so_far += file_size
                files_copied += 1

                # Add the copied file to the set
                copied_files.add(source_file)
            else:
                break

    print(f"Created batch {i + 1} with {files_copied} files and a total size of {batch_size_so_far / (1024 * 1024):.2f} MB")

print(f"Created {num_batches} batch folders in {root_folder}.")
