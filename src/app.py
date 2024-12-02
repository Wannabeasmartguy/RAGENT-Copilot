import os
import sys
import time
import queue
import json
# import signal
import pystray
import tkinter as tk
import keyboard
import pyautogui
import threading
import customtkinter as ctk
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox
from pystray import MenuItem as item, Menu
from plyer import notification
from PIL import Image
from typing import Generator, Union
from utils.chat.llm import LLM
from loguru import logger
from utils.chat.prompts import get_task_prompts, get_editor_prompts
from utils.log.logger_config import setup_logger
# TODO：先使用环境变量控制语言
from utils.chat.prompts import LANGUAGE

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
        self.root.geometry("400x400")
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


# def signal_handler(sig, frame):
#     logger.info("Ctrl+C pressed. Exiting...")
#     sys.exit(0)

# keyboard.add_hotkey("ctrl+c", signal_handler)


def show_notification():
    notification.notify(
        app_name="RAGENT-Copilot",
        app_icon="assets\RAGenT_logo.ico",  # Replace with the path to your icon file
        # ticker="RAGENT-Copilot",
        title="应用启动",
        message="RAGENT-Copilot 已启动",
        timeout=10  # 通知显示的时间（秒）
    )


def monitor_keys(app):
    try:
        if not keyboard.add_hotkey("ctrl+shift+space", app.toggle_window):
            logger.error("Failed to register hotkey")
            return
        while True:
            time.sleep(1)
    except Exception as e:
        logger.error(f"Exception in key monitoring: {e}")
    finally:
        keyboard.remove_hotkey("ctrl+shift+space")
        keyboard.unhook_all()


def exit_action(icon, item):
    icon.stop()
    logger.info("Exited application from tray icon")
    root.quit()


def restart_action(icon, item):
    icon.stop()
    logger.info("Restarting application from tray icon")
    python = sys.executable
    os.execl(python, python, *sys.argv)


def create_tray_icon(app):
    image = Image.open("assets\RAGenT_logo.png")  # Replace "icon.png" with the path to your icon file
    menu = (item('Settings', open_settings_window), item('Restart', restart_action), item('Quit', exit_action),)
    icon = pystray.Icon("name", image, "RAGENT-Copilot", menu)

    # 显示通知
    show_notification()

    # Clicking the icon to the left will open the settings window.
    def on_clicked(icon, query):
        if str(query) == "Open Settings":
            open_settings_window()
    icon.menu = Menu(item('Open Settings', on_clicked, default=True, visible=False), *icon.menu)
    
    icon.run()


def open_settings_window():
    settings_window_queue.put(True)

def handle_settings_window_queue():
    try:
        while True:
            settings_window_queue.get_nowait()
            create_settings_window()
    except queue.Empty:
        root.after(100, handle_settings_window_queue)

def create_settings_window():
    settings_window = ctk.CTkToplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x550")
    settings_window.minsize(400, 550)
    settings_window.maxsize(550, 600)

    # 创建两个tab
    settings_tabview = ctk.CTkTabview(master=settings_window, width=400)
    settings_tabview.pack(padx=20, pady=20)
    tab_general = settings_tabview.add("General")
    tab_advanced = settings_tabview.add("Advanced")
    settings_tabview.set("General")  # set currently visible tab

    # General settings
    ctk.CTkLabel(tab_general, text="Settings", font=("Roboto", 20)).pack(padx=10, pady=10)
    ctk.CTkLabel(tab_general, text="Enter your model provider settings here:").pack(padx=10, pady=5)
    # create a list to store labels and entries
    general_labels_map = {
        "Base URL:": "base_url",
        "API Key:": "api_key",
        "Model:": "model",
    }
    general_labels = []
    general_entries = []
    # Base URL
    base_url_label = ctk.CTkLabel(tab_general, text="Base URL:")
    base_url_label.pack(padx=10, pady=5, anchor='w')
    general_labels.append(base_url_label)
    base_url_entry = ctk.CTkEntry(tab_general, width=300)
    base_url_entry.pack(padx=10, pady=5)
    general_entries.append(base_url_entry)
    # Api key
    api_key_label = ctk.CTkLabel(tab_general, text="API Key:")
    api_key_label.pack(padx=10, pady=5, anchor='w')
    general_labels.append(api_key_label)
    api_key_entry = ctk.CTkEntry(tab_general, show="*", width=300)
    api_key_entry.pack(padx=10, pady=5)
    general_entries.append(api_key_entry)
    # Model name
    model_label = ctk.CTkLabel(tab_general, text="Model:")
    model_label.pack(padx=10, pady=5, anchor='w')
    general_labels.append(model_label)
    model_entry = ctk.CTkEntry(tab_general, width=300)
    model_entry.pack(padx=10, pady=5)
    general_entries.append(model_entry)

    # Advanced settings
    advanced_labels_map = {
        "Temperature:": "temperature",
        "Max Tokens:": "max_tokens",
        "Top P:": "top_p",
        "Frequency Penalty:": "frequency_penalty"
    }
    advanced_labels = []
    advanced_entries = []
    ctk.CTkLabel(tab_advanced, text="Advanced Settings for models", font=("Roboto", 20)).pack(padx=10, pady=10)
    # Temperature
    temperature_label = ctk.CTkLabel(tab_advanced, text="Temperature:")
    temperature_label.pack(padx=10, pady=5, anchor='w')
    advanced_labels.append(temperature_label)
    temperature_entry = ctk.CTkEntry(tab_advanced, width=300)
    temperature_entry.pack(padx=10, pady=5)
    advanced_entries.append(temperature_entry)
    # Max tokens
    max_tokens_label = ctk.CTkLabel(tab_advanced, text="Max Tokens:")
    max_tokens_label.pack(padx=10, pady=5, anchor='w')
    advanced_labels.append(max_tokens_label)
    max_tokens_entry = ctk.CTkEntry(tab_advanced, width=300)
    max_tokens_entry.pack(padx=10, pady=5)
    advanced_entries.append(max_tokens_entry)
    # Top P
    top_p_label = ctk.CTkLabel(tab_advanced, text="Top P:")
    top_p_label.pack(padx=10, pady=5, anchor='w')
    advanced_labels.append(top_p_label)
    top_p_entry = ctk.CTkEntry(tab_advanced, width=300)
    top_p_entry.pack(padx=10, pady=5)
    advanced_entries.append(top_p_entry)
    # Frequency penalty
    frequency_penalty_label = ctk.CTkLabel(tab_advanced, text="Frequency Penalty:")
    frequency_penalty_label.pack(padx=10, pady=5, anchor='w')
    advanced_labels.append(frequency_penalty_label)
    frequency_penalty_entry = ctk.CTkEntry(tab_advanced, width=300)
    frequency_penalty_entry.pack(padx=10, pady=5)
    advanced_entries.append(frequency_penalty_entry)

    # 加载已保存的设置
    def load_settings():
        if os.path.exists("settings/settings.json"):
            with open("settings/settings.json", "r") as file:
                settings = json.load(file)
                
                # 填充常规设置
                for label, entry in zip(general_labels, general_entries):
                    key = general_labels_map[label.cget("text")]
                    if key in settings["general"]:
                        entry.delete(0, tk.END)
                        entry.insert(0, settings["general"][key])
                
                # 填充高级设置
                for label, entry in zip(advanced_labels, advanced_entries):
                    key = advanced_labels_map[label.cget("text")]
                    if key in settings["advanced"]:
                        entry.delete(0, tk.END)
                        entry.insert(0, settings["advanced"][key])

    # 调用加载设置函数
    load_settings()
    
    def save_settings():
        # 将所有条目构建为一个可序列化的字典
        # 根据 general_labels_map 和 advanced_labels_map 构建字典
        settings = {
            "general": {},
            "advanced": {}
        }

        # 更新"general"部分
        general_data = {general_labels_map[label.cget("text")]: entry.get() for label, entry in zip(general_labels, general_entries)}
        settings["general"].update({k: v for k, v in general_data.items() if v != ""})

        # 更新"advanced"部分
        advanced_data = {advanced_labels_map[label.cget("text")]: entry.get() for label, entry in zip(advanced_labels, advanced_entries)}
        settings["advanced"].update({k: v for k, v in advanced_data.items() if v != ""})

        if not os.path.exists("settings"):
            os.makedirs("settings")
        # 保存之前，检查general是否全部为空，如果是，则不保存
        if all(entry.get() == "" for entry in general_entries):
            logger.warning("No general settings provided, not saving.")
            # 弹出提示框
            messagebox.showwarning("Warning", "No general settings provided, not saving.")
            return
        with open("settings/settings.json", "w") as file:
            json.dump(settings, file)
            logger.info("Settings saved successfully.")
            # 弹出提示框

        response = messagebox.askyesno("Settings Saved", "Settings saved successfully.\nDo you want to close all windows?", default=messagebox.NO)
        if response:
            settings_window.destroy()
            # 关闭其他窗口的代码可以在这里添加
        else:
            # 返回的代码可以在这里添加
            pass
        # settings_window.destroy()

    def reset_settings():
            # 删除本地的settings.json文件
            if os.path.exists("settings/settings.json"):
                os.remove("settings/settings.json")
                logger.info("Settings reset successfully.")
                # 弹出提示框
                messagebox.showinfo("Settings Reset", "Settings reset successfully.")
            else:
                logger.warning("No settings file found, nothing to reset.")
                # 弹出提示框
                messagebox.showwarning("Warning", "No settings file found, nothing to reset.")

    save_button = ctk.CTkButton(settings_window, text="Save", command=save_settings)
    save_button.pack(padx=10, pady=10)

    reset_button = ctk.CTkButton(settings_window, text="Reset", command=reset_settings)
    reset_button.pack(padx=10, pady=10)

settings_window_queue = queue.Queue()


def main():
    global root
    root = ctk.CTk()
    app = CopilotApp(root)
    app.create_right_click_menu()  # Add this line to create the right-click menu

    # Start key monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_keys, args=(app,))
    monitor_thread.daemon = True
    monitor_thread.start()

    # Start tray icon in a separate thread
    tray_thread = threading.Thread(target=create_tray_icon, args=(app,))
    tray_thread.daemon = True
    tray_thread.start()

    # Handle settings window queue in the main thread
    root.after(100, handle_settings_window_queue)

    root.mainloop()


if __name__ == "__main__":
    main()