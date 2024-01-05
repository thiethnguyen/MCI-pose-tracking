import os
import json

# Specify the path to your JSON file
json_file_path = (r"Z:\Sensors_Folder\Pose_estimation_output\pose\Sing\Cam1_PCI\json_files\Cam1_PCI-PD"
                  r"-combined_output.json")  # Replace 'your_json_file.json' with the actual file path

# Specify the folder path where you want to save the JSON files
output_folder = 'output_jsons'  # Replace 'output_jsons' with your desired folder name

base_name = os.path.basename(json_file_path)

# Load the JSON data from the file
with open(json_file_path, 'r') as json_file:
    original_data = json.load(json_file)

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Now, you have the original JSON data loaded into the 'original_data' variable
# You can iterate through the frames and process the data as needed, as shown in the previous example
# Iterate through each frame and create a separate JSON file for each
for frame_id, frame_data in original_data.items():
    # Create a dictionary for the current frame
    frame_dict = {frame_id: frame_data}

    # Generate a JSON filename for the frame (e.g., frame_1.json)
    filename = os.path.join(output_folder, f"base_name_{int(frame_id)-1}.json")

    # Save the frame data to a JSON file
    with open(filename, "w") as json_file:
        json.dump(frame_dict, json_file, indent=4)

print("JSON files created for each frame.")
