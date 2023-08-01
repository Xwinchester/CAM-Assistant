import configparser
import importlib.util
import tkinter as tk
from os import path, getlogin, makedirs
from tkinter import messagebox

class Launcher:

    C_DRIVE_PATH = path.join ("C:\\Users", getlogin (), "CamAssistant")
    CONFIG_FILE = path.join(C_DRIVE_PATH, "config.ini")
    MAIN_FILE =  "CamAssistant.py"

    def __init__(self):
        self.SOURCE_PATH = None
        self.check_c_drive ()
        self.validate_config()
        self.run()

    def check_c_drive(self):
        """
        checks to see if cam assistant fold exists inside the users drive
        if not, it will create the folder
        :return:
        """
        if not path.exists (self.C_DRIVE_PATH):
            self.make_directory()

    def make_directory(self):
        """
        creates the cam assistant folder inside the c drive under the active user
        :return:
        """
        makedirs (self.C_DRIVE_PATH)
        print (f"Created folder: {self.C_DRIVE_PATH}")

    def validate_config(self):
        """
        checks to see if config file exists, if exists, reads files
        if not, creates and sets files
        :return:
        """
        if not path.exists(self.CONFIG_FILE):
            self.create_config()
        self.read_config()

    def create_config(self):
        config = configparser.ConfigParser ()
        config['PATHS'] = self.JSON_PATHS
        with open (self.CONFIG_FILE, 'w') as configfile:
            config.write (configfile)

    def read_config(self):
        config = configparser.ConfigParser ()
        config.read (self.CONFIG_FILE)
        self.SOURCE_PATH = config['Paths']['source']

    def get_current_version(self):
        try:
            filePath = path.join (self.C_DRIVE_PATH, self.CONFIG_FILE)
            config = configparser.ConfigParser ()
            config.read (filePath)
            version = config.get ('GENERAL', 'version')
            return version.strip ()
        except (configparser.Error, FileNotFoundError):
            return '-1'

    def messageBox(self, title="", message=""):
        """
        :param title: title to the message box if an error or need to inform the user of something
        :param message: message for the box to inform the user
        :return:
        """
        # Create the Tkinter window
        window = tk.Tk ()
        window.withdraw ()  # Hide the main window
        # Show the message box
        #messagebox.askquestion (title=title, message=message)
        messagebox.showwarning(title, message)
        # Close the Tkinter window
        window.destroy ()

    def run(self):
        try:
            spec = importlib.util.spec_from_file_location ("module_name", path.join(self.SOURCE_PATH, self.MAIN_FILE))
            module = importlib.util.module_from_spec (spec)
            spec.loader.exec_module (module)
            function = getattr (module, "main")
            function ()
        except Exception as e:
            self.messageBox("Error", e)

if __name__ == '__main__':
    Launcher ()
