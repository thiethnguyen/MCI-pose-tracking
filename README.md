# Mother-child interaction pose tracking
version v1.0.

## Some introductions
The pose estimation and tracking in this project are based on two methods:
- [Openpose](https://github.com/CMU-Perceptual-Computing-Lab/openpose): for multi-person pose estimation.
- [YOLOv7](https://github.com/WongKinYiu/yolov7): for face/head detection.


## Requirements
The code in this repository has been tested to work well on systems with these prerequisites:
- (Required) Operating system: Windows
- (Required) Software: Anaconda installed
- (Optional) Nvidia GPU with suitable drivers installed


## How to set up the environment for the code to run:
- **_Step 1_**: Download the code in this project. The code will be saved in _MCI_pose_tracking_ folder.
- **_Step 2_**: Download Openpose pretrained models. Further instructions for this step can be found in the later part of this README. The downloaded data (after unzipping) will be saved in _openpose_ folder.
- **_Step 3_**: Copy the folders _bin, include, lib, models_ in the _openpose_ folder to the _MCI_pose_tracking_ folder:
![](/openpose_to_reaching_detection.png)
- **_Step 4_**: Download YOLO pretrained model for head detection from _Head_Detection_ folder [here](https://drive.google.com/drive/folders/1h9QPRJ2J7aaTRaOsk_39KJ3PdILR85NY), and put into _Head_Detection/yolov7-main_. 
- **_Step 5_**: Set up the python environments for running the model. See detailed instructions for this step in the later part of this README.

#### Instructions for **_Step 2_** - downloading necessary Openpose pretrained models:
1. (For computer with Nvidia GPU) For maximum speed, you should use OpenPose in a machine with a Nvidia GPU version. If so, you must upgrade your Nvidia drivers to the latest version (in the Nvidia "GeForce Experience" software or its [website](https://www.nvidia.com/Download/index.aspx)).
2. **Download the latest OpenPose version from the [Releases](https://github.com/CMU-Perceptual-Computing-Lab/openpose/releases) section. (If GPU is going to be used, download the file "openpose-1.7.0-binaries-win64-gpu-python3.7-flir-3d_recommended.zip".)**
3. **Follow the Instructions.txt file inside the downloaded zip file to download the models required by OpenPose (about 500 Mb).**
4. (Optional) Then, you can run OpenPose from the PowerShell command-line by following [doc/01_demo.md](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/01_demo.md).

Further instructions for **_Step 2_** can be found via [Windows Portable Demo](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation/0_index.md#windows-portable-demo).

If the links for downloading the models fail (which may occur while running the .bat file), you can download the entire _models_ folder from [here](https://drive.google.com/drive/u/2/folders/1DyzjWh5O6CCH_BXdIyXTJoJJarkd3wSy).

#### Instructions for **_Step 5_** - setting up new python environments:

**_Step 5.1_**. The new environment for OpenPose related-code must use python 3.7 (same python version as the released openpose models). The sequential commands (to be run on a Command Prompt or an Anaconda Prompt) for creating, activating a new environment named 'mci_pose' and then installing required packages are shown as follows: (Do all these commands in the root directory)

`conda create -n mci_pose python=3.7`

`conda activate mci_pose`

`pip install -r requirements.txt`

**_Step 5.2_**. This step involves setting up the environment to execute YOLOv7-related code. Although 'mci_pose' can be used, creating a new environment is essential due to PyTorch's utilization with GPU. Ensuring compatibility between Python, PyTorch, and CUDA versions is crucial for Torch's functionality using CUDA. Hence, it's advisable to install a new environment with a more recent Python version (for instance, 3.9 or later). To create a secondary environment, go to _Head_Detection/yolov7-main_ and install a new environment using the provided 'requirements.txt' file. 

`conda create -n mci_head python=3.9`

`conda activate mci_head`

`pip install -r requirements.txt`

By default, the provided installation installs PyTorch for CPU. To install PyTorch with GPU, uninstall torch, torchvision, and torchaudio first. Then, install the appropriate version of PyTorch with GPU support for your system from the PyTorch [website](https://pytorch.org/). 


## How to run the code on a video, image, or folder of videos/images:
1. Open an Anaconda Prompt window and navigate to the project directory.
2. Activate the Conda environment created in **_Step 5.1_** (called 'mci_pose').
3. Run the main Python script by typing:
```
python main.py --input "path/to/file_or_folder" --output "path/to/output_folder" --yolo-env 'mci_head'
```

Where:

`--input` specifies the path to a video/image file or folder containing input videos/images.

`--output` specifies the output folder path.

`--yolo-env 'mci_head'` passes the name of the YOLO environment ('mci_head' in this case).

To simply try out the code on the example video included in the repository, call 
```
python main.py --yolo-env 'mci_head'
```

## How to inteprete the results:
The pose estimation and tracking results will be saved to the output folder you specified. For each input video, there will be a corresponding output subfolder using the video's file name.

Within each video output subfolder, there are 4 key subfolders:

- _face_outputs/_ - Contains the output video of the face/head detection.
- _json_files/_ - Contains body pose keypoint data with ID information in JSON format. The file with "combined_output" suffix has integrated pose + head detections.
- _output_videos/_ - Contains the output video of the pose estimation.
- _matlab_files/_ - Contains data files in ".mat" format. Two smaller subfolders can be found: "0" contains the keypoints of mom and "1" contains the keypoints of baby.

## Additional materials used in the project:
The example video in _data/list_of_files_ is a shorten version of the video named "Impatient Children|How to Deal With it Effectively|" from Youtube: https://www.youtube.com/watch?v=BM6DPRo_QfE. The video is under license "Creative Commons Attribution license (reuse allowed)".
