import cv2
from datetime import datetime

filename = r"Z:\Thiet\Github\MCI_pose_tracking\data\list_of_files\VLOG - Day in the Life With Our Twin Boys.mp4"
cap = cv2.VideoCapture(filename)  # Read Frame
fps = cap.get(cv2.CAP_PROP_FPS)  # Extract the frame per second (fps)

height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # height
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # width

origin = "00:00:00"  # the origin
start = "00:14:33"  # specify start time in hh:mm:ss 0*3600+57*60, 0*3600+59*60
end = "00:14:39"  # specify end time in hh:mm:ss

origin_time = datetime.strptime(origin, "%H:%M:%S")  # origin
start_time = datetime.strptime(start, "%H:%M:%S")  # start time
end_time = datetime.strptime(end, "%H:%M:%S")  # end time

start_frame = fps * (start_time - origin_time).total_seconds()  # get the start frame
end_frame = fps * (end_time - origin_time).total_seconds()  # get the end frame


start_frame_0 = 100  # get the start frame
end_frame_0 = 830  # get the end frame

start_frame_1 = 1730  # get the start frame
end_frame_1 = 2460  # get the end frame

# video writer
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
out1 = cv2.VideoWriter(r"Z:\Thiet\Github\MCI_pose_tracking\data\list_of_files\VLOG - Day in the Life With Our Twin "
                       r"Boys_cut.mp4",
                       fourcc, fps, (width, height))

counter = 1  # set counter
while cap.isOpened():  # while the cap is open

    ret, frame = cap.read()  # read frame
    if frame is None:  # if frame is None
        break

    frame = cv2.resize(frame, (width, height))  # resize the frame
    if start_frame <= counter <= end_frame:  # check for range of output
        out1.write(frame)  # output

    # cv2.imshow("Frame", frame)  #display frame
    key = cv2.waitKey(1) & 0xFF

    counter += 1  # increase counter
    if counter % 500 == 0:
        print(counter)

# release the output and cap
out1.release()
cv2.destroyAllWindows()
