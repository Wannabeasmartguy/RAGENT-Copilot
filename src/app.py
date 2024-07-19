import sys
import time
import signal
import tkinter as tk
import keyboard
import pyautogui
import threading
import customtkinter as ctk
from concurrent.futures import ThreadPoolExecutor
from typing import Generator, Union
from utils.llm import LLM
from loguru import logger
from utils.prompts import get_task_prompts, get_editor_prompts
from utils.logger_config import setup_logger
# TODO：先使用环境变量控制语言
from utils.prompts import LANGUAGE

import pyperclip


class CopilotApp:
    """
    CopilotApp is a GUI application that provides a set of buttons to perform various text processing tasks.
    It uses a language model (LLM) to generate responses based on clipboard content and displays the results in a new window.
    """

    def __init__(self, root: ctk.CTk):
        self.llm = LLM()
        self.prompts = get_task_prompts()
        self.editor_prompts = get_editor_prompts()
        self.root = root
        self._initialize_root_window()
        self._create_layout()
        self._create_buttons()
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.drag_data = {"x": 0, "y": 0}  # Store the drag data
        self.border_color = "#363537"
        self.is_pinned = False
        self.temp_generated_text = ""  # Temporary storage for generated text

    def _initialize_root_window(self):
        """
        Initialize the main application window with specific attributes.
        """
        self.root.title("Button Tree")
        self.root.geometry("400x300")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", self.root["bg"])
        self.root.withdraw()  # Hide the window initially
        self.root.bind("<Button-1>", self.start_drag_root)
        self.root.bind("<B1-Motion>", self.do_drag_root)

    def _create_layout(self):
        """
        Create the layout for the application, including frames for icon and buttons.
        """
        self.icon_frame = tk.Frame(self.root, width=100, height=100, bg=self.root["bg"])
        self.icon_frame.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

        self.buttons_frame = tk.Frame(self.root, bg=self.root["bg"])
        self.buttons_frame.grid(row=0, column=1, padx=10, pady=10)

        # Load the icon image
        self.icon_image = tk.PhotoImage(file="./assets/sparkles_72x72.png")

        self.icon_label = tk.Label(
            self.icon_frame,
            image=self.icon_image,
            bg=self.root["bg"],
            height=72,
            width=72,
        )
        self.icon_label.pack()

    def _create_buttons(self):
        """
        Create buttons for different tasks and add them to the buttons frame.
        """
        button_options = {
            "width": 160,
            "height": 40,
            "corner_radius": 10,
            "fg_color": "white",
            "font": ("Roboto", 18, "normal"),
            "text_color": "#363537",
            "hover_color": "gray",
            "border_width": 2,
            "border_color": "#363537",
        }

        tasks = [
            ("Summarize", 0),
            ("Translate", 5),
            ("Fix Grammar", 2),
            ("Extract Keywords", 3),
            ("Explain", 4),
            ("Compose Mail", 1),
        ]

        colors = ["#ED7D3A", "#1E90FF", "#0CCE6B", "#DCED31", "#EF2D56", "#8E24AA"]

        for i, (text, index) in enumerate(tasks):
            button_options["border_color"] = colors[i]
            button_options["hover_color"] = colors[i]
            button = ctk.CTkButton(
                self.buttons_frame,
                text=text,
                command=lambda i=index: self.on_button_click(i, color=colors[i]),
                **button_options,
            )
            button.grid(row=i, column=0, pady=5)

    def toggle_window(self):
        """
        Toggle the visibility of the main application window.
        """
        if self.root.state() == "withdrawn":
            x, y = pyautogui.position()
            self.root.geometry(f"+{x-50}+{y-150}")
            self.root.deiconify()
        else:
            self.root.withdraw()

    def on_button_click(self, task_index, color=None):
        """
        Handle button click events by triggering the corresponding task.
        """
        self.toggle_window()
        self.executor.submit(self.handle_button_click, task_index)
        self.border_color = color

    def handle_button_click(self, task_index):
        """
        Execute the task corresponding to the clicked button.
        """
        prompt = self.prompts[task_index]["prompt"]
        # 模仿用户点击Ctrl+C
        pyautogui.hotkey('ctrl', 'c')
        # 读取剪贴板内容作为用户输入
        prompt = prompt.format(text=pyperclip.paste(), language=LANGUAGE)
        logger.info(f"Prompt: {prompt}")
        generated_text = self.llm.generate(prompt)
        logger.info(f"Generated text: {generated_text}")
        self.root.after(0, self.show_generated_text, generated_text)

    def show_generated_text(self, text: Union[Generator, str]):
        """
        Display the generated text in a new, borderless window near the mouse cursor.
        """
        new_window = tk.Toplevel(self.root)
        new_window.title("Generated Text")
        new_window.geometry("1200x900")
        new_window.overrideredirect(True)
        new_window.attributes("-transparentcolor", new_window["bg"])

        # Set the window position to the mouse cursor
        x, y = pyautogui.position()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Adjust the window position to stay within screen boundaries
        window_width = 600
        window_height = 450

        x = min(max(0, x - window_width // 2), screen_width - window_width)
        y = min(max(0, y - window_height // 2), screen_height - window_height)

        new_window.geometry(f"+{x}+{y}")

        center_frame = ctk.CTkFrame(
            new_window,
            fg_color="white",
            corner_radius=15,
            border_width=2,
            border_color=self.border_color,
            width=560,
            height=410,
        )
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, bordermode="outside")

        # Add a blank horizontal bar for the pin button and close button
        blank_bar = ctk.CTkFrame(center_frame, height=40, fg_color="white")
        blank_bar.pack(fill="x", padx=10, pady=(10, 0))

        # Add pin button
        self.pin_button = ctk.CTkButton(
            blank_bar,
            text="📌",
            command=lambda: self.toggle_pin(new_window),
            width=30,
            height=30,
            corner_radius=15,
            fg_color="white",
            font=("Roboto", 16, "normal"),
            text_color="#363537",
            hover_color="gray",
            border_width=2,
            border_color="#363537",
        )
        self.pin_button.pack(side="left", padx=10)

        # Add close button
        close_button = ctk.CTkButton(
            blank_bar,
            text="❎",
            command=new_window.destroy,
            width=30,
            height=30,
            corner_radius=15,
            fg_color="white",
            font=("Roboto", 16, "normal"),
            text_color="#363537",
            hover_color="gray",
            border_width=2,
            border_color="#363537",
        )
        close_button.pack(side="right", padx=10)

        text_box = ctk.CTkTextbox(
            center_frame,
            wrap=tk.WORD,
            font=("Roboto", 18),
            corner_radius=10,
            fg_color="#212230",
            text_color="#FFFFFF",
            width=560,
            height=320,  # Reduce the height to account for the blank bar
        )
        text_box.pack(expand=True, fill="both", padx=(10, 10), pady=(10, 10))

        # According to the type of text, insert it into the text box
        if isinstance(text, str):
            logger.debug(f"Text")
            # update the temporary generated text, which will be used for editing
            self.temp_generated_text = text
            text_box.insert(tk.END, text)
        elif hasattr(text, '__iter__'):
            logger.debug(f"Generator")
            self.insert_text_generator(text_box, text, new_window)

        text_box.configure(state="disabled")

        # Create buttons for editing text
        edit_buttons_frame = ctk.CTkFrame(center_frame, fg_color="white")
        edit_buttons_frame.pack(padx=10, pady=10)

        edit_button_options = {
            "width": 100,
            "height": 40,
            "corner_radius": 10,
            "fg_color": "white",
            "font": ("Roboto", 16, "normal"),
            "text_color": "#363537",
            "hover_color": "gray",
            "border_width": 2,
            "border_color": "#363537",
        }

        edit_button_fg_colors = ["#ED7D3A", "#1E90FF", "#0CCE6B", "#EF2D56", "#DCED31"]

        edit_tasks = ["Casual", "Formal", "Professional", "Technical", "Simple"]

        for i, task in enumerate(edit_tasks):
            edit_button_options["border_color"] = edit_button_fg_colors[i]
            edit_button_options["hover_color"] = edit_button_fg_colors[i]
            edit_button = ctk.CTkButton(
                edit_buttons_frame,
                text=task,
                command=lambda t=task: self.edit_text(t, self.temp_generated_text, text_box),
                **edit_button_options,
            )
            edit_button.grid(row=0, column=i, padx=5)

        def on_focus_out(event):
            if not new_window.focus_get() and not self.is_pinned:
                new_window.destroy()

        new_window.bind("<FocusOut>", on_focus_out)
        new_window.focus_force()

        # Bind mouse events for dragging the window
        center_frame.bind(
            "<Button-1>", lambda event: self.start_drag_new_window(event, new_window)
        )
        center_frame.bind("<B1-Motion>", lambda event: self.do_drag_new_window(event, new_window))

        # Bind mouse events for dragging the blank bar
        blank_bar.bind(
            "<Button-1>", lambda event: self.start_drag_new_window(event, new_window)
        )
        blank_bar.bind("<B1-Motion>", lambda event: self.do_drag_new_window(event, new_window))

    def insert_text_generator(self, text_box, text_generator, new_window):
        if not text_box.winfo_exists():
            logger.debug("Text box does not exist")
            return
        try:
            chunk = next(text_generator)
            logger.debug(f"Generated chunk: {chunk}")
            text_box.configure(state="normal")  # Make the text box editable

            content = chunk.choices[0].delta.content
            self.temp_generated_text += content
            text_box.insert(tk.END, content)

            text_box.see(tk.END)
            text_box.update()
            text_box.configure(state="disabled")  # Make the text box read-only again
            new_window.after(100, self.insert_text_generator, text_box, text_generator, new_window)
        except StopIteration:
            logger.debug(f"StopIteration")
            text_box.configure(state="disabled")  # Ensure the text box is read-only after generator ends
            pass

    def toggle_pin(self, window):
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            window.attributes("-topmost", True)
            self.pin_button.configure(text="📌 Pinned")
        else:
            window.attributes("-topmost", False)
            self.pin_button.configure(text="📌")

    def start_drag_root(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def do_drag_root(self, event):
        x = self.root.winfo_x() + event.x - self.drag_data["x"]
        y = self.root.winfo_y() + event.y - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def start_drag_new_window(self, event, window):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def do_drag_new_window(self, event, window):
        x = window.winfo_x() + event.x - self.drag_data["x"]
        y = window.winfo_y() + event.y - self.drag_data["y"]
        window.geometry(f"+{x}+{y}")

    def edit_text(self, task, text, text_box):
        """
        Handle text editing tasks. Implement the logic as needed.
        """
        self.show_loading_overlay(text_box)
        self.executor.submit(self.async_edit_text, task, text, text_box)

    def async_edit_text(self, task, text, text_box):
        editor_prompt = next(
            (item for item in self.editor_prompts if item["editor"] == task), None
        )

        if editor_prompt:
            prompt = editor_prompt["prompt"]
            prompt = prompt.format(text=text, language=LANGUAGE)
            logger.info(f"Prompt for {task}: {prompt}")
            generated_text = self.llm.generate(prompt)
            
            # Handle generator
            if isinstance(generated_text, str):
                pass
            else:
                generated_text_itered = ""
                for chunk in generated_text:
                    message = chunk.choices[0].delta.content
                    logger.debug(f"Chunk message is {message}")
                    generated_text_itered += message
                generated_text = generated_text_itered

            logger.info(f"Generated text for {task}: {generated_text}")
            pyperclip.copy(generated_text)
            self.root.after(0, self.update_text_box, text_box, generated_text)

    def show_loading_overlay(self, text_box):
        overlay = tk.Frame(text_box, bg="#212230")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        loading_label = tk.Label(overlay, text="Loading...", font=("Roboto", 18), bg="#212230", fg="white")
        loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.overlay = overlay  # Store the overlay reference

    def update_text_box(self, text_box, generated_text):
        text_box.configure(state="normal")
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, generated_text)
        text_box.configure(state="disabled")
        self.overlay.destroy()  # Remove the overlay

    def create_right_click_menu(self):
        """
        Create a right-click menu with options to toggle the window and exit the application.
        """
        self.right_click_menu = tk.Menu(self.root, tearoff=0)
        self.right_click_menu.add_command(label="Close Window", command=self.toggle_window)
        self.right_click_menu.add_command(label="Exit App", command=self.root.quit)

        def show_right_click_menu(event):
            try:
                self.right_click_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.right_click_menu.grab_release()

        self.root.bind("<Button-3>", show_right_click_menu)


def signal_handler(sig, frame):
    logger.info("Ctrl+C pressed. Exiting...")
    sys.exit(0)


def monitor_keys(app):
    try:
        keyboard.add_hotkey("ctrl+space", app.toggle_window)
        while True:
            time.sleep(1)
    except Exception as e:
        logger.error(f"Exception in key monitoring: {e}")
    finally:
        keyboard.unhook_all()


def main():
    root = ctk.CTk()
    app = CopilotApp(root)
    app.create_right_click_menu()  # Add this line to create the right-click menu

    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Start key monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_keys, args=(app,))
    monitor_thread.daemon = True
    monitor_thread.start()

    root.mainloop()


if __name__ == "__main__":
    logger.add("app.log", rotation="10 MB")
    main()