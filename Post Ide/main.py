import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import configparser
from postEngine import PostEngine


class Configuration:

    def __init__(self):
        self.FILE_NAME = "post.ini"
        self.__load_config()


    def __load_config(self):
        # Check if config file exists
        try:
          # File exists, load it
          self.CONFIG = configparser.ConfigParser()
          self.CONFIG.read(self.FILE_NAME)
          print(self.CONFIG.get("GENERAL", "name"))
        except Exception as e:
            print(e)
            exit(0)
class CamAssistantApp(tk.Tk):
    TITLE = "CAM Assistant Post"

    def __init__(self):
        super().__init__()
        self.post_engine = PostEngine()
        #Configuration()
        self.title(self.TITLE)
        self.dark_mode_var = tk.BooleanVar()
        self.dark_mode_var.set(True)
        self.__setup_ui()
        self.__configure_colors()
        self.__open_file("C:/Users/dwinc/Desktop/test.nci")  # for debugging only, avoids opening file

    def __setup_ui(self):
        # Create a menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open File", command=self.__open_file)
        file_menu.add_command(label="Save File", command=self.__save_file)
        menubar.add_cascade(label="File", menu=file_menu)

        # Dark mode menu
        dark_mode_menu = tk.Menu(menubar, tearoff=False)
        dark_mode_menu.add_checkbutton(label="Dark Mode", variable=self.dark_mode_var, command=self.__toggle_dark_mode)
        menubar.add_cascade(label="Options", menu=dark_mode_menu)

        # Script menu
        script_menu = tk.Menu(menubar, tearoff=False)
        script_menu.add_command(label="Run Script", command=self.__run_script)
        script_menu.add_command(label="Test Script", command=self.__run__test_script)
        menubar.add_cascade(label="Script", menu=script_menu)

        # Reset menu
        menubar.add_command(label="Reset", command=self.__reset_text)

        self.left_text = tk.Text(self, wrap="word", width=80, height=30)
        self.left_text.pack(fill=tk.BOTH, expand=True)

        # Store the original content of the left text frame
        self.original_content = ""
    def __configure_colors(self):
        if self.dark_mode_var.get():
            self.__configure_dark_mode_colors()
        else:
            self.__configure_light_mode_colors()

    def __configure_dark_mode_colors(self):
        self.config(bg="#1f1f1f")
        self.left_text.config(bg="#121212", fg="#f1f1f1", insertbackground="white")

    def __configure_light_mode_colors(self):
        self.config(bg="#f1f1f1")
        self.left_text.config(bg="white", fg="black", insertbackground="black")

    def __toggle_dark_mode(self):
        self.__configure_colors()

    def __open_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(filetypes=[("Cam File", "*.nci"), ("All Files", "*.*")])
            print(file_path)
        if file_path:
            with open(file_path, 'r') as file:
                # reads nci file
                content = file.read()
                self.post_engine.input_nci(content)
                # updates the editor with the code
                self.__update_file(content)

    def __update_file(self, content):
        self.left_text.delete("1.0", tk.END)
        self.left_text.insert(tk.END, content)

    def __save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".nci", filetypes=[("Cam File", "*.nci"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                content = self.__get_text()
                file.write(content)

    def __reset_text(self):
        # Reset the left text frame to the original content
        self.left_text.delete("1.0", tk.END)
        self.left_text.insert(tk.END, self.post_engine.get_raw_nci_string())

    def __get_text(self):
        return self.left_text.get("1.0", tk.END).strip()

    def __run__test_script(self):
        file = "scripts//script.py"
        try:
            with open(file, 'r') as script_file:
                script = script_file.read()
                content = self.post_engine.post(script)
                self.__update_file(content)
        except Exception as e:
            messagebox.showerror("Error", f"Error running the script\n{e}")
    def __run_script(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Script", "*.py"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as script_file:
                    script = script_file.read()

                # Create a dictionary with the left text content
                script_globals = {'nci_file': self.post_engine.get_raw_nci_string()}

                # Execute the script in the specified globals dictionary
                exec(script, script_globals)

                """
                    nci_file  <- use this for the text from the body of the text file
                """

                # Check if the script defines a main function
                if 'main' in script_globals:
                    # Call the main function and pass the left text content to it
                    # function will return new code to update the screen
                    content = script_globals['main']()
                    self.__update_file(content)
            except Exception as e:
                messagebox.showerror("Error", f"Error running the script: {e}")

def test():
    PE = PostEngine()
    file_path = "C:/Users/dwinc/Desktop/test.nci"
    with open (file_path, 'r') as file:
        # reads nci file
        content = file.read ()
    PE.input_nci (content)
    with open ("scripts//script.py", 'r') as file:
        script = file.read()
    post = PE.post(script)
    PE.test()


if __name__ == "__main__":
    toTest = True
    if toTest:
        test()
    else:
        app = CamAssistantApp()
        app.mainloop()
