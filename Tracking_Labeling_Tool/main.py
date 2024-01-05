import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import os
import json
import re


def path_to_new_ext(file_path, new_ext=".json"):
    # Extract the directory path and file name from the original path
    directory_path, original_file_name = os.path.split(file_path)

    # Change the file extension to ".json" to create the new file name
    new_file_name = os.path.splitext(original_file_name)[0] + new_ext

    # Join the directory path and the new file name to get the JSON file path
    new_file_path = os.path.join(directory_path, new_file_name)

    # Now, json_file_path contains the path to the JSON file with the same name
    # print(json_file_path)

    return new_file_path


# Function to update the "baby_ma_id" based on "ID"
def update_baby_ma_id(data, target_id, new_baby_ma_id):
    # Iterate through the keys in the outer dictionary
    for outer_key, outer_value in data.items():
        # Check if the inner dictionary has a "Data" key
        if "Data" in outer_value:
            # Access the data inside the "Data" key
            data_inside_data_key = outer_value["Data"]

            # Now, data_inside_data_key contains the list of data entries
            # You can iterate through this list if there are multiple entries
            for entry in data_inside_data_key:
                # Access specific attributes inside each entry
                if target_id == entry["ID"]:
                    entry["baby_ma_id"] = int(new_baby_ma_id)
                    # Print or process the attributes as needed
                    # print('ID:', entry["ID"])
                    # print("baby_ma_id:", entry["baby_ma_id"])
                    return True

    print('update_baby_ma_id failed, nothing changed!', data)
    return False  # Return False if ID not found


def set_initial_text(entry_widget, initial_text):
    entry_widget.insert(0, initial_text)


class ImageViewer:
    def __init__(self, root):
        self.tips_window = None
        self.current_image = None
        self.image_path = None
        self.tree = None
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("1200x720")

        # Create a frame for the top section
        ############################################################
        # ###################### TOP FRAME  ########################
        ############################################################
        self.top_frame = ttk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        # Create the folder path label and add it to the top frame
        self.folder_path_label = ttk.Label(self.top_frame, text="   Working folder: ", anchor="center")
        self.folder_path_label.pack(side=tk.LEFT)

        # Create a "Tips" button and add it to the top frame
        self.tips_button = ttk.Button(self.top_frame, text="Tips", command=self.show_tips)
        self.tips_button.pack(side=tk.RIGHT)

        # Create a PanedWindow to divide the window into two parts
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(expand=True, fill="both")

        # Create a frame for displaying images (left side)
        ############################################################
        # ############### IMAGE FRAME (left side) ##################
        ############################################################
        self.image_frame = ttk.Frame(self.paned_window)
        self.image_frame.pack(expand=True, fill="both")
        # self.paned_window.add(self.image_frame, weight=60)

        # Create a Label to display the filename
        self.filename_label = ttk.Label(self.image_frame, text="")
        self.filename_label.pack()

        self.load_button = ttk.Button(self.image_frame, text="Choose Folder", command=self.choose_folder)
        self.load_button.pack()

        # Create a Canvas widget for displaying the image with scrollbars
        self.image_canvas = tk.Canvas(self.image_frame)

        # Create a scrollbar for the vertical direction
        self.image_v_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        self.image_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_canvas.config(yscrollcommand=self.image_v_scrollbar.set)

        # Create a scrollbar for the horizontal direction
        self.image_h_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        self.image_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.image_canvas.config(xscrollcommand=self.image_h_scrollbar.set)

        self.image_canvas.pack(fill="both", expand=True)

        self.image_label = ttk.Label(self.image_canvas)
        self.image_label_id = self.image_canvas.create_window(0, 0, anchor=tk.NW, window=self.image_label)

        # Create a frame for the slider
        self.slider_frame = ttk.Frame(self.image_frame)
        self.slider_frame.pack(side=tk.BOTTOM, fill="x")

        # Create a slider
        self.image_slider = ttk.Scale(self.slider_frame, from_=0, to=0, command=self.change_image)
        self.image_slider.pack(fill="x", expand=True)

        # Create a frame for loading JSON files (right side)
        ############################################################
        # ############### JSON FRAME (right side) ##################
        ############################################################
        self.json_frame = ttk.Frame(self.paned_window)
        self.json_frame.pack(expand=True, fill="both")
        # self.paned_window.add(self.json_frame, weight=40)

        # Create a Label to display the filename
        self.json_filename_label = ttk.Label(self.json_frame, text="")
        self.json_filename_label.pack()

        self.load_json_button = ttk.Button(self.json_frame, text="Choose JSON File",
                                           command=self.choose_json_file)
        self.load_json_button.config(state="disabled")
        self.load_json_button.pack()

        # Create two sub-frames within the JSON frame
        # ================================================
        # ============= JSON FRAME - top =================
        self.json_top_frame = ttk.Frame(self.json_frame)
        self.json_top_frame.pack(expand=True, fill="both")

        # =====================================
        # ====== JSON FRAME - top - left ======
        # Create a grid within the top subframe to divide it into left and right sections
        self.json_top_left_frame = ttk.Frame(self.json_top_frame)
        self.json_top_left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.label_frame = ttk.Frame(self.json_top_left_frame)
        self.label_frame.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.text_box_frame = ttk.Frame(self.json_top_left_frame)
        self.text_box_frame.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Initialize labels with empty strings
        self.labels = []
        self.text_boxes = []

        # Create a "Save" button
        self.save_button = ttk.Button(self.json_top_left_frame, text="Save", command=self.save_values)
        self.save_button.grid(row=1, column=1, padx=5, pady=10)

        # =====================================
        # ====== JSON FRAME - top - right ======
        self.json_top_right_frame = ttk.Frame(self.json_top_frame)
        self.json_top_right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Create a textbox, button, and labels in the right part
        self.json_label1 = ttk.Label(self.json_top_right_frame, text="Baby ID range:")
        self.json_label1.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.json_lbl_id_min = ttk.Label(self.json_top_right_frame, text="Min ID:")
        self.json_lbl_id_min.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.json_textbox_id_min = ttk.Entry(self.json_top_right_frame, width=10)
        self.json_textbox_id_min.grid(row=1, column=1, padx=3, pady=3)

        self.json_lbl_id_max = ttk.Label(self.json_top_right_frame, text="Max ID:")
        self.json_lbl_id_max.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.json_textbox_id_max = ttk.Entry(self.json_top_right_frame, width=10)
        self.json_textbox_id_max.grid(row=2, column=1, padx=3, pady=3)

        self.json_button = ttk.Button(self.json_top_right_frame, text="Update", command=self.update_id_range)
        self.json_button.grid(row=3, column=0, padx=5, pady=5)
        self.json_button.config(state="disabled")

        self.some_text_on_id_lbl = ttk.Label(self.json_top_right_frame, text="Advice:")
        self.some_text_on_id_lbl.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.some_text_on_id = ttk.Entry(self.json_top_right_frame, width=33)
        self.some_text_on_id.grid(row=5, rowspan=3, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        self.display_id_advice()
        self.some_text_on_id.config(state="readonly")

        # ================================================
        # ============= JSON FRAME - middle ==============
        self.json_mid_frame = ttk.Frame(self.json_frame)
        self.json_mid_frame.pack(expand=True, fill="both")
        self.json_mid_saved_file = ttk.Label(self.json_mid_frame, text="Previous saved: None")
        # self.json_mid_saved_file.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.json_mid_saved_file.pack()

        # ================================================
        # ============= JSON FRAME - bottom ==============
        self.json_bottom_frame = ttk.Frame(self.json_frame)
        self.json_bottom_frame.pack(expand=True, fill="both")

        # Bottom json text view
        self.json_text = tk.Text(self.json_bottom_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.json_text.pack(fill="both", expand=True)

        # Create a vertical scrollbar for the JSON viewer
        self.json_v_scrollbar = tk.Scrollbar(self.json_text, orient=tk.VERTICAL, command=self.json_text.yview)
        self.json_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.json_text.config(yscrollcommand=self.json_v_scrollbar.set)

        self.json_h_scrollbar = ttk.Scrollbar(self.json_text, orient=tk.HORIZONTAL, command=self.json_text.xview)
        self.json_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.json_text.config(xscrollcommand=self.json_h_scrollbar.set)

        self.image_list = []
        self.current_index = 0
        self.zoom_factor = 0.5
        self.mouse_over_json = False

        root.bind("<Key>", self.key_pressed)
        root.bind("<MouseWheel>", self.zoom_image)

        self.paned_window.add(self.image_frame, weight=5)
        self.paned_window.add(self.json_frame, weight=1)

        # Bind events for resizing
        self.paned_window.bind("<Button-1>", self.start_resize)
        self.paned_window.bind("<B1-Motion>", self.resize)

        # Bind mouse events for image dragging
        self.image_label.bind("<ButtonPress-1>", self.start_drag)
        self.image_label.bind("<B1-Motion>", self.drag_image)

        # Bind events for mouse enter and leave in the JSON viewer
        self.json_frame.bind("<Enter>", self.on_mouse_enter_json)
        self.json_frame.bind("<Leave>", self.on_mouse_leave_json)

        self.resizing = False
        self.resize_x = 0

        self.dragging = False
        self.start_x = 0
        self.start_y = 0

        # Number of rows to create in advance (adjust as needed)
        self.num_rows_to_create = 5

        # Create the initial rows of labels, text boxes, and buttons
        self.create_initial_rows()

        # Bind the MouseWheel event to the text boxes
        for text_box in self.text_boxes:
            text_box.bind("<MouseWheel>", self.on_mouse_wheel)

        self.id_range = [-1, 1]
        set_initial_text(self.json_textbox_id_min, str(self.id_range[0]))
        set_initial_text(self.json_textbox_id_max, str(self.id_range[1]))
        self.json_textbox_id_min.config(state="readonly")
        self.json_textbox_id_max.config(state="readonly")

    def show_tips(self):
        if self.tips_window is None or not self.tips_window.winfo_exists():
            # Create a new window for displaying tips
            self.tips_window = tk.Toplevel(self.root)
            self.tips_window.title("Tips")

            # Increase the size of the tips window
            self.tips_window.geometry("400x300")

            # Create a Text widget to display the tips
            tips_text = tk.Text(self.tips_window, wrap=tk.WORD, height=15, width=40)
            tips_text.pack(fill=tk.BOTH, expand=True)

            # Add your tips as multiple lines of text
            tips_text.insert(tk.END, "Here are some tips on how to use this application:\n\n")
            tips_text.insert(tk.END,
                             "Tip 1: In the image frame, you can use the mouse wheel to zoom in/out the image and "
                             "drag to"
                             "move the image freely.\n")
            tips_text.insert(tk.END,
                             "\n")
            tips_text.insert(tk.END,
                             "Tip 2: Hover your mouse over an ID text box (no need to click inside it), and you can use"
                             "the mouse wheel to change the baby ID.\n")
            tips_text.insert(tk.END,
                             "\n")
            tips_text.insert(tk.END,
                             "Tip 3: Press \"A\"/\"D\" to go to previous/next image while saving the JSON. Press "
                             "\"left\"/\"right\" arrows to go to previous/next image without saving the JSON.\n")

            # Make the new window non-resizable
            self.tips_window.resizable(False, False)

            # Center the new window on top of the main window
            self.tips_window.geometry("+{}+{}".format(
                self.root.winfo_x() + (self.root.winfo_width() // 2) - 200,
                self.root.winfo_y() + (self.root.winfo_height() // 2) - 150
            ))
        else:
            if self.tips_window.winfo_exists():
                # If the tips window is still open, bring it to the foreground
                self.tips_window.deiconify()
        #     else:
        #         # If the tips window is closed, set tips_window to None
        #         self.tips_window = None

    def choose_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.load_images_from_folder(folder_path)

    def load_images_from_folder(self, folder_path):
        self.image_list = []
        self.current_index = 0
        self.zoom_factor = 1.0

        # Update the folder_path label
        self.folder_path_label.config(text='   Working folder: ' + folder_path)

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_path = os.path.join(folder_path, filename)
                self.image_list.append(image_path)
        # print(self.image_list)
        self.image_list = sorted(self.image_list, key=lambda x: int(os.path.splitext(x)[0].split("_")[-1]))
        # print(self.image_list)

        image_0_path = self.image_list[0]
        image_0 = Image.open(image_0_path)
        width, height = image_0.size
        self.zoom_factor = 720 / width  # first image shown should have width = 720

        # Update the slider range when images are loaded
        self.image_slider.config(from_=0, to=len(self.image_list) - 1)

        if self.image_list:
            self.show_image(0)
            self.auto_load_json_file(path_to_new_ext(self.image_path))

    def create_initial_rows(self):
        for _ in range(self.num_rows_to_create):
            # Create a label
            label = ttk.Label(self.label_frame, text="")
            label.grid(row=len(self.labels), column=0, padx=5, pady=5, sticky="e")
            self.labels.append(label)

            # Create a text box
            text_box = ttk.Entry(self.text_box_frame, width=10)
            text_box.grid(row=len(self.text_boxes), column=0, padx=5, pady=5, sticky="w")
            text_box.config(state="readonly")
            self.text_boxes.append(text_box)

    def start_resize(self, event):
        self.resizing = True
        self.resize_x = event.x

    def resize(self, event):
        if self.resizing:
            self.resize_x = event.x

    def choose_json_file(self):
        json_file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if json_file_path:
            with open(json_file_path, 'r') as json_file:
                json_data = json.load(json_file)
                self.display_json(json.dumps(json_data, indent=4))

                # self.reset_labels_and_text_boxes()

                # Update the table based on JSON data
                self.update_label(json_data)

                # Store the JSON file path for saving changes
                self.json_file_path = json_file_path

            # Update the filename label
            self.json_filename_label.config(text=os.path.basename(self.json_file_path))

    def auto_load_json_file(self, json_file_path):
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                self.json_data = json.load(json_file)
                self.display_json(json.dumps(self.json_data, indent=4))

                # self.reset_labels_and_text_boxes()

                # Update the table based on JSON data
                self.update_label(self.json_data)

                # Store the JSON file path for saving changes
                self.json_file_path = json_file_path
            # Update the filename label
            self.json_filename_label.config(text=os.path.basename(self.json_file_path))

    def reset_labels_and_text_boxes(self):
        # Clear labels
        for label in self.label_frame.winfo_children():
            label.config(text="")

        # Clear text boxes
        for text_box in self.text_boxes:
            text_box.delete(0, tk.END)

    def decrease_value(self, index):
        current_value = int(self.text_boxes[index].get())
        self.text_boxes[index].delete(0, tk.END)
        self.text_boxes[index].insert(0, str(current_value - 1))

    def increase_value(self, index):
        current_value = int(self.text_boxes[index].get())
        self.text_boxes[index].delete(0, tk.END)
        self.text_boxes[index].insert(0, str(current_value + 1))

    def update_label(self, json_data):
        self.reset_labels_and_text_boxes()
        # Extract "ID"s and "baby_ma_id"s and populate labels and text boxes
        # Extract "ID"s and "baby_ma_id"s and populate labels, text boxes, and buttons
        for i, (key, value) in enumerate(json_data.items()):
            if "Data" in value:
                data = value["Data"]
                for j, entry in enumerate(data):
                    if "ID" in entry and "baby_ma_id" in entry:
                        id_value = entry["ID"]
                        baby_ma_id_value = entry["baby_ma_id"]

                        # Show the label, text box, and buttons for this row
                        self.labels[i * len(data) + j].config(text=id_value)
                        self.text_boxes[i * len(data) + j].config(state="normal")
                        self.text_boxes[i * len(data) + j].delete(0, tk.END)
                        self.text_boxes[i * len(data) + j].insert(0, baby_ma_id_value)
                        # self.text_boxes[i * len(data) + j].config(state="readonly")
                        # self.enable_buttons(i * len(data) + j)

    def save_values(self):
        # Iterate through the labels and text boxes to save values
        for i in range(len(self.labels)):
            id_value = str(self.labels[i]["text"])  # Get the ID from the label
            if id_value != "":
                baby_ma_id_value = re.search(r'-?\d+', self.text_boxes[
                    i].get()).group()  # Get the new baby_ma_id value from the text box

                # print(id_value, baby_ma_id_value)

                update_baby_ma_id(self.json_data, id_value, baby_ma_id_value)
                # print(self.json_data)
        # Save the updated JSON data to the JSON file
        # json_file_path = "/path/to/your/json_file.json"  # Replace with your JSON file path
        with open(self.json_file_path, 'w') as json_file:
            json.dump(self.json_data, json_file, indent=4)

        self.json_mid_saved_file.config(text=os.path.basename(self.json_file_path) + ' saved!')

    def update_id_range(self):
        # self.id_range = [-1, 1]
        self.id_range[0] = int(self.json_textbox_id_min.get())
        self.id_range[1] = int(self.json_textbox_id_max.get())
        pass

    def display_json(self, content):
        self.json_text.config(state=tk.NORMAL)
        self.json_text.delete("1.0", tk.END)
        self.json_text.insert(tk.END, content)
        self.json_text.config(state=tk.DISABLED)

    def display_id_advice(self):
        content = 'Baby = 1,  ' + '\n' + 'Mom = 0,  ' + '\n' + 'Others = -1'
        set_initial_text(self.some_text_on_id, content)
        # self.some_text_on_id.config(state=tk.NORMAL)
        # self.some_text_on_id.delete("1.0", tk.END)
        # self.some_text_on_id.insert(tk.END, content)
        # self.some_text_on_id.config(state=tk.DISABLED)

    def show_image(self, index):
        if 0 <= index < len(self.image_list):
            self.image_path = self.image_list[index]
            image = Image.open(self.image_path)
            width, height = image.size
            new_width = int(width * self.zoom_factor)
            new_height = int(height * self.zoom_factor)

            self.current_image = ImageTk.PhotoImage(image.resize((new_width, new_height), Image.LANCZOS))

            # Update the label and canvas with the new image
            self.image_label.config(image=self.current_image)
            self.image_canvas.config(scrollregion=self.image_canvas.bbox(tk.ALL))

            # Update the filename label
            self.filename_label.config(text=os.path.basename(self.image_path))

            self.current_index = index

    def change_image(self, event):
        index = int(self.image_slider.get())
        self.show_image(index)
        self.auto_load_json_file(path_to_new_ext(self.image_path))

    def key_pressed(self, event):
        key = event.keysym.lower()
        if key == 'a' and (event.state & 0x4) != 0:
            print('ctrl+a')
            self.custom_function_for_ctrl_a()  # Handle Ctrl+A
        elif key == "a" and (event.state & 0x4) == 0:
            print('only a')
            self.prev_image()
        elif key == "d":
            print('d')
            self.next_image()
        elif key == 'left':
            print('left')
            self.prev_image(save=False)
        elif key == 'right':
            print('right')
            self.next_image(save=False)

    def prev_image(self, save=True):
        if save:
            self.save_values()
        if self.current_index > 0:
            self.show_image(self.current_index - 1)
            self.auto_load_json_file(path_to_new_ext(self.image_path))
            # Update the image slider position
            self.image_slider.set(self.current_index)

    def next_image(self, save=True):
        if save:
            self.save_values()
        if self.current_index < len(self.image_list) - 1:
            self.show_image(self.current_index + 1)
            self.auto_load_json_file(path_to_new_ext(self.image_path))
            # Update the image slider position
            self.image_slider.set(self.current_index)

    def zoom_image(self, event):
        if self.current_image and not self.mouse_over_json:
            delta = event.delta
            self.zoom_factor += delta / 1200
            self.show_image(self.current_index)

    def on_mouse_enter_json(self, event):
        self.mouse_over_json = True

    def on_mouse_leave_json(self, event):
        self.mouse_over_json = False

    def start_drag(self, event):
        self.dragging = True
        self.start_x = event.x
        self.start_y = event.y

    def drag_image(self, event):
        if self.dragging:
            # Calculate the movement offsets
            dx = event.x - self.start_x
            dy = event.y - self.start_y

            # Move the image label based on the offsets
            self.image_canvas.move(self.image_label_id, dx, dy)

            # Update the starting position
            self.start_x = event.x
            self.start_y = event.y

    def on_mouse_wheel(self, event):
        # Get the widget where the event occurred
        widget = event.widget

        # Only handle the event if it's a text box
        if isinstance(widget, ttk.Entry):
            current_value = widget.get()
            try:
                current_value = int(current_value)
                new_value = current_value + event.delta // 120  # Adjust the increment as needed
                if int(new_value) < self.id_range[0]:
                    new_value = self.id_range[0]
                elif int(new_value) > self.id_range[1]:
                    new_value = self.id_range[1]

                widget.delete(0, tk.END)
                widget.insert(0, str(new_value))
            except ValueError:
                # Handle non-integer values here if needed
                pass

    def custom_function_for_ctrl_a(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    viewer = ImageViewer(root)

    root.mainloop()
