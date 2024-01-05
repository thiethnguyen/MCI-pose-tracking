import os
import sys
import argparse

# input_path = r"W:\LEAP_PCI\Singapore_PCI\Sensors Final Test\LP016"
# output_path = r"X:\PCI-PD\Sensors Final Test\LP016"
# yolo_env_name = 'yolov7_head'

try:
    # Get the path to the current Python environment
    env_path = sys.prefix
    # Extract the environment name from the path
    env_name = os.path.basename(env_path)
    print("Current environment name:", env_name)
except Exception as e:
    print('Error when getting the current env:', e)
    env_name = 'base'

# Create the parser
my_parser = argparse.ArgumentParser(description='Process some arguments')
# Add the arguments
my_parser.add_argument('--input',
                       type=str,
                       help='the file(s) or folder of input images and/or videos',
                       default=os.path.join(os.getcwd(), r"data\list_of_files"))
my_parser.add_argument('--output',
                       type=str,
                       help='the file(s) or folder of output images and/or videos',
                       default=os.path.join(os.getcwd(), r"data\output_files"))
my_parser.add_argument('--yolo-env',
                       type=str,
                       help='the conda env for running yolov7',
                       default=env_name)

# Execute the parse_args() method
args = my_parser.parse_args()
input_path = args.input
output_path = args.output
yolo_env_name = args.yolo_env

# Check if the folder has subfolders
if any(os.path.isdir(os.path.join(output_path, item)) for item in os.listdir(output_path)):
    print("Output folder contains subfolders, consider removing subfolders or creating a new output folder.")
    sys.exit(1)  # Exit the script if subfolders are found

print('===============================================================================================================')
print('=============================================== POSE ESTIMATION +==============================================')
command_1 = r'cd "Pose_Estimation"'
command_2 = f'python openpose_main.py --input "{input_path}" --output "{output_path}" --noheader'
command = command_1 + ' && ' + command_2
print(command)

try:
    exit_code = os.system(command)
except os.error as e:
    print(f"Command '{e.cmd}' failed with error: {e.stderr}")
    exit(1)
# Check the exit code
if exit_code == 0:
    print('. . . DONE! . . . ')
else:
    print(f"Command failed with exit code: {exit_code}")
    exit(1)

print('===============================================================================================================')
print('================================================ HEAD DETECTION ===============================================')
command_yolo_1 = r'cd "Head_Detection"'
command_yolo_2 = f'conda run -n {yolo_env_name} python detect_face.py --input-path "{input_path}" ' \
                 f'--txt-output-directory "{output_path}" ' \
                 f'--yolo-weight-path "yolov7-main\\best_sensors_24_8_8.pt" --img-dir-input ' \
    # f'> yolo_detection_log.txt 2>&1'  # conda run -n test_py37

command_yolo = command_yolo_1 + ' && ' + command_yolo_2
print(command_yolo)

print('. . . RUNNING . . . ')
try:
    exit_code = os.system(command_yolo)
except os.error as e:
    print(f"Command '{e.cmd}' failed with error: {e.stderr}")
    exit(1)
# Check the exit code
if exit_code == 0:
    print('. . . DONE! . . . CHECK LOGGING IN Head_Detection/yolo_detect_log.txt')
else:
    print(f"Command failed with exit code: {exit_code}")
    exit(1)

print('===============================================================================================================')
print('============================================ POSE-HEAD INTEGRATION ============================================')
command_int_1 = r'cd "Pose_Head_Integration"'
command_int_2 = f'python integration_use_yolo_face.py --input-pose-folder "{output_path}" ' \
    # f'> output_json_combine.txt 2>&1'

command_int = command_int_1 + ' && ' + command_int_2
print(command_int)

try:
    exit_code = os.system(command_int)
except os.error as e:
    print(f"Command '{e.cmd}' failed with error: {e.stderr}")
    exit(1)
# Check the exit code
if exit_code == 0:
    print('. . . DONE! . . . ')
else:
    print(f"Command failed with exit code: {exit_code}")
    exit(1)

print('===============================================================================================================')
print('=============================================== POST FILTERING ================================================')
command_fil_1 = r'cd "Filtering"'
command_fil_2 = f'python data_preprocessing.py --input-pose-folder "{output_path}" ' \
    # f'> output_preprocessing.txt 2>&1'

command_fil = command_fil_1 + ' && ' + command_fil_2
print(command_fil)

try:
    exit_code = os.system(command_fil)
except os.error as e:
    print(f"Command '{e.cmd}' failed with error: {e.stderr}")
    exit(1)
# Check the exit code
if exit_code == 0:
    print('. . . DONE! . . . ')
else:
    print(f"Command failed with exit code: {exit_code}")
    exit(1)
