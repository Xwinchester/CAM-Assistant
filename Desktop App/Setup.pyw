import os
import shutil
import configparser
import tkinter as tk
from tkinter import messagebox

def copy_specific_files(source_folder, destination_folder, config_file, section):
    # Read the config file and extract the file names to move
    config = configparser.ConfigParser(allow_no_value=True, delimiters='=')
    config.read(config_file)
    files_to_move = [key for key in config[section] if key.strip()]

    # Ensure the destination folder exists or create it
    create_folder(destination_folder)

    # Loop through the files in the source folder
    for file_name in os.listdir(source_folder):
        source_file_path = os.path.join(source_folder, file_name)
        lower_file_name = file_name.lower()

        # Check if the file should be moved based on the config file
        if lower_file_name in files_to_move:
            destination_file_path = os.path.join(destination_folder, file_name)

            # Perform the copy operation
            shutil.copy(source_file_path, destination_file_path)
            print(f"Copied: {source_file_path} -> {destination_file_path}")

def create_folder(folder_path):
    # Check if the folder exists and create it if it doesn't
    if os.path.exists(folder_path):
        print(f'{folder_path} folder already exists')
    else:
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

def messageBox( title="", message="", option="info"):
        """
        :param title: title to the message box if an error or need to inform the user of something
        :param message: message for the box to inform the user
        :return:
        """
        # Create the Tkinter window
        window = tk.Tk ()
        window.withdraw ()  # Hide the main window
        # Show the message box
        if option.lower() == "yesno":
            answer = messagebox.askyesno (title, message)
        else:
            answer = messagebox.showinfo(title, message)
        # Close the Tkinter window
        window.destroy ()
        return answer

def update_profiles():
    file_path = "profiles.txt"

    # Check if the "profiles.txt" file exists
    if not os.path.exists(file_path):
        # If the file doesn't exist, create it and add the current user to the list
        with open(file_path, "w") as file:
            file.write(os.getlogin() + "\n")
    else:
        # If the file exists, read the content and check if the current user is already in the list
        with open(file_path, "r") as file:
            content = file.read()
            profiles = content.split()

            current_user = os.getlogin()
            if current_user not in profiles:
                # Add the current user to the list
                with open(file_path, "a") as file:
                    file.write(current_user + "\n")

# Example usage:
if __name__ == "__main__":
    # stores username, using just to see how many people and who are using to help them
    update_profiles()

    # File path from where all the files are coming from
    source_folder_path = os.path.join("C:\\", "Users", os.getlogin(), "Desktop", "Setup Folder")

    # Destination file path, C drive under the user and creating a CamAssistn folder
    destination_folder_path = os.path.join("C:\\", "Users", os.getlogin(), "CamAssistant")
    
    # Destination file path, C drive under the user's desktop
    c_drive_desktop_path = os.path.join("C:\\", "Users", os.getlogin(), "Desktop")
    
    config_file_path = "Setup.ini"

    # Copy files based on the "User" section in the config file
    copy_specific_files(source_folder_path, destination_folder_path, config_file_path, "User")

    # Copy files based on the "Desktop" section in the config file
    copy_specific_files(source_folder_path, c_drive_desktop_path, config_file_path, "Desktop")

    messageBox("CamAssistant", "Setup complete!\nRun 'CamAssistantLauncher.pyw' on your Desktop to run\nThank you for using my program!")
