import cv2

import imageio

from _0_data_constants import *

cap = cv2.VideoCapture(FOLDER + 'Camcorder 2 DEmo_output.avi')
image_lst = []
no_frame = 0
while no_frame < 1100:
    ret, frame = cap.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if no_frame+1 >= 996 and no_frame + 1 <= 1084:
        image_lst.append(frame_rgb)

    cv2.imshow('a', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    no_frame += 1
    print(no_frame)

cap.release()
cv2.destroyAllWindows()

# Convert to gif using the imageio.mimsave method
imageio.mimsave(FOLDER + 'video.gif', image_lst, fps=60)