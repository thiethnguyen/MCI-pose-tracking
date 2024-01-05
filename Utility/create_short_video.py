import cv2

video_input='C:\\Users\\Home - Jupiter\\Desktop\\Nancy Pelosi claps for President Trump.mp4'
video_output='C:\\Users\\Home - Jupiter\\Desktop\\Nancy Pelosi claps for President Trump_short.avi'
capture = cv2.VideoCapture(video_input)
# print(self.video_file)
if capture.isOpened():  # Checks the stream
    frameSize = (int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                      int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))

frame_width = int(capture.get(3))
frame_height = int(capture.get(4))
frame_rate = (capture.get(5))
print(frame_rate,frame_height,frame_width)

size = (frame_width, frame_height)

result_video = cv2.VideoWriter(video_output,
                                        cv2.VideoWriter_fourcc(*'MJPG'),
                                        1, size)

frame_no = 0
while frame_no < 3:
    result, currentFrame = capture.read()

    if not result:
        print("Can't receive frame (stream end?). Exiting ...")
        print("==========================================================================")
        break
    result_video.write(currentFrame)
    frame_no += 1
