import math
from tkinter import *
from tkinter import filedialog, ttk, messagebox
from enum import Enum
import json
import os
import subprocess
import configparser
import urllib.request
import smtplib
from datetime import datetime


class ColorScheme(Enum):
  DARK = {
    'data_frame_background': "#454954",
    'data_frame_font': 'light gray',
    'data_frame_entry_background': 'white',
    'data_frame_entry_font': 'black',
    'data_frame_button_background': 'gray',
    'data_frame_button_font': 'black',
    "button_frame_background": "#141417",
    'button_frame_font': 'gray',
    'checkbox_font': 'black',
    "logo_frame_background": "#141417",
    'logo_frame_font': 'gray',
    "button_background": "gray",
    "button_font": "black",
    "message_background":"gray",
    "message_font":"black"
  }
  LIGHT = {
    'data_frame_background': "white",
    'data_frame_font': 'black',
    'data_frame_entry_background': 'white',
    'data_frame_entry_font': 'black',
    'data_frame_button_background': 'light gray',
    'data_frame_button_font': 'black',
    "button_frame_background": "gray",
    'button_frame_font': 'black',
    'checkbox_font': 'black',
    "logo_frame_background": "gray",
    'logo_frame_font': 'black',
    "button_background": "light gray",
    "button_font": "black",
    "message_background":"light gray",
    "message_font":"black"
  }

class BaseApp:
  """
  a class to store app data that every app will use. 
  """

  def __init__(self, app, frame, data=None):
    # store instance of the app
    self.app = app
    # store the frame we can use with these apps
    self.frame = frame
    # store data if it exists, either be None or json data
    self.data = data

    self.__create_title()

  def __create_title(self):
    # sets title to current app
    title = self.app.CURRENT_APP.value.title()

    # if current app is home, set the title to welcome
    if self.app.CURRENT_APP == Apps.HOME:
      title = f"Welcome to {self.app.APP_NAME}"
    # create the label
    lbl = Label(self.frame, text=title, font=(None, 30))
    # pack the label, home is centered, rest are on the top
    if self.app.CURRENT_APP == Apps.HOME:
      lbl.pack(expand=True, anchor='center')
    else:
      lbl.pack()

class Home(BaseApp):
    """
    creates the welcome home page
    """
    def __init__(self, app, frame, data=None):
      super().__init__(app, frame, data)


class ThreadExpert(BaseApp):

  def __init__(self, app, frame, data):
    super().__init__(app, frame, data=data)

    # creates the lists for all of the thread data
    self.__get_thread_data()

    # creates the entire frame that the user can see
    self.__create_frame()

    # updates all of the boxes to show data right when the app is opened
    self.__update_entries()

  def __get_thread_data(self):
      # grab all of the thread data
      self.THREAD_DATA = [thread for thread in self.data]
      # create the list for the drop down
      self.THREADS = [thread['size'] for thread in self.THREAD_DATA]

  def __create_frame(self):
    # creates a frame to store all of the labels & entries
    frame = Frame(self.frame)
    frame.pack()

    # a list of all of the labels for the entry boxes    
    # keep the enter chamfer size as last in this list
    labels = [
      "Minor Diameter:", "Major Diameter:", "Threads / Inch (Pitch):", "Cutting Tap:", "Roll Tap:",
      "Breakout Chamfer:", "Contour Chamfer:", "Enter Chamfer:"
    ]
    self.ENTRIES = []
    btn_index = 0

    # creates label for the drop down mwnu
    Label(frame, text="Select Threads:", font=(None, 14)).grid(row=0, column=0)

    # creates string var for the drop down
    self.SELECTED_THREAD = StringVar(frame)

    # create the the option menu
    self.SELECTED_THREAD.set(self.THREADS[0])
    optionMenu = OptionMenu(frame,
                            self.SELECTED_THREAD,
                            *self.THREADS,
                            command=self.__update_entries)
    optionMenu.config(font=(None, 15))
    optionMenu['menu'].config(font=(None, 15))
    optionMenu.grid(pady=5, row=0, column=1)

    # creates all of the entry boxes to store the thread data
    for index, lbl in enumerate(labels, 1):
      Label(frame, text=lbl, font=(None, 14)).grid(pady=2, row=index, column=0)
      entry = Entry(frame, font=(None, 14))
      if index != len(labels):
        entry.configure(state='disabled')
        entry.bind("<KeyRelease>", self.__update_chamfers)
      entry.bind("<Return>", self.__bind_entries)
      entry.grid(pady=2, row=index, column=1)
      self.ENTRIES.append(entry)
      btn_index += 1

    # setup calculate button
    self.ENTER_BTN = Button(frame,
                            text="Calculate Chamfer",
                            command=self.__update_entries,
                            width=35,
                            font=(None, 14))
    self.ENTER_BTN.grid(pady=5, row=btn_index + 1, column=0, columnspan=2)

  # Define callback function for "Enter" button
  def __update_entries(self, events=""):
    # grabs chamfer size entered, if nothing. sets to .010 as a good default
    selected_thread = self.SELECTED_THREAD.get()
    thread_data = next(
      (thread
       for thread in self.THREAD_DATA if thread["size"] == selected_thread),
      None)
    if thread_data:
      # minor diameter
      self.__update_entrie_box(self.ENTRIES[0], self.__set_minor_diameter(thread_data["minor diameter"]))
      #major diameter
      self.__update_entrie_box(self.ENTRIES[1], thread_data["major diameter"])
      # Threads Per Inch
      self.__update_entrie_box(self.ENTRIES[2], self.__set_feed(thread_data["threads per inch"]))
      # Cutting Tap
      self.__update_entrie_box(self.ENTRIES[3], self.__set_tap(thread_data["cutting tap"]))
      # Roll Tap
      self.__update_entrie_box(self.ENTRIES[4], self.__set_tap(thread_data["roll tap"]))
      # Chamfers
      self.__update_chamfers()

  def __set_feed(self, threads):
    try:
      tpi = float(threads)
      pitch = round(1 / tpi, 5)
      return f"{threads} ( {pitch} )"
    except:
      return f"{threads} ()"

  def __set_minor_diameter(self, thread):
    return f"{thread['low']} - {thread['high']}"

  def __set_tap(self, tap):
    if tap['diameter'] == 0:
      return ""
    return f"{tap['diameter']} ( {tap['size']} )"

  def __update_entrie_box(self, box, data):
    box.configure(state="normal")
    box.delete(0, END)
    box.insert(0, data)
    box.configure(state="disabled")

  def __update_chamfers(self, events=''):
    user_chamfer_size = self.ENTRIES[7].get()
    if user_chamfer_size == "":
      self.ENTRIES[7].delete(0, END)
      self.ENTRIES[7].insert(0, ".010")
      user_chamfer_size = self.ENTRIES[7].get()
    selected_thread = self.SELECTED_THREAD.get()
    thread_data = next(
      (thread
       for thread in self.THREAD_DATA if thread["size"] == selected_thread),
      None)
    if thread_data:
      chamfer_size = self.__caclulate_chamfer(thread_data["minor diameter"],thread_data['major diameter'], user_chamfer_size)
      self.__update_entrie_box(self.ENTRIES[5], chamfer_size['plunge'])
      self.__update_entrie_box(self.ENTRIES[6], chamfer_size['contour'])

  def __caclulate_chamfer(self, minor, major, chamfer_size):
    result = {}
    rounding = 4
    try:
      chamfer = float(chamfer_size)
      minor = float((minor['high'] + minor['low']) / 2)
      major = float(major)
      result['contour'] = round((major - minor) + chamfer, rounding)
      result['plunge'] = round(major + (chamfer * 2), rounding)
    except:
      result['contour'] = "NULL"
      result['plunge'] = "NULL"
    return result

  def __bind_entries(self, event):
    self.ENTER_BTN.invoke()

class PlaceholderEntry (Entry):
  def __init__(self, master=None, placeholder="Enter your text here", fg='gray', *args, **kwargs):
    super ().__init__ (master, *args, **kwargs)
    self.placeholder = placeholder
    self.fg = fg
    self.bind ("<FocusIn>", self.on_entry_click)
    self.bind ("<FocusOut>", self.on_focus_out)
    self.on_focus_out (event="")

  def on_entry_click(self, event):
    if self.get () == self.placeholder:
      self.delete (0, "end")
      self.config (fg='black')

  def on_focus_out(self, event):
    if not self.get ():
      self.insert (0, self.placeholder)
      self.config (fg=self.fg)

  def grab_text(self):
    txt = self.get()
    # if text is placeholder ignore it
    if txt == self.placeholder:
      return ""
    return self.__format_text(txt)

  def __format_text(self, txt):
    if "name" in self.placeholder.lower():
      return txt.title().replace(" ", "_")
    return txt.upper().replace(" ", "_")

class FolderFactory(BaseApp):
  """
  creates the welcome home page
  """    
  def __init__(self, app, frame, data=None):
      super().__init__(app, frame, data)
      self.__load_folders()

      # create file path label
      self.__create_file_path_label()

      self.__create_frame()

  
  def __create_frame(self):
      # create frame to hold folders
      partFrame = Frame(self.frame)
      partFrame.pack(padx=10)

      # create IntVar to hold whethe to open folder or not
      self.CREATE_PART_FOLDER_VAR = IntVar()
      self.CREATE_PART_FOLDER_VAR.set(1)

      # create label to open folder or not
      create_folder_checkbox = Checkbutton(partFrame, text="Open Part Folder?", variable=self.CREATE_PART_FOLDER_VAR, font=(None, 16))
      create_folder_checkbox.grid(pady=5, row=0, columnspan=4)

      # create section to hold part number & part name
      font = (None, 12)
      part_number_label = Label (partFrame, text="Part Number:", font=font)

      # part number section, label and placeholder widget
      part_number_label = Label(partFrame, text="Part Number:", font=font)
      part_number_label.grid(padx=4,pady=4, row=1, column=0)
      self.PART_NUMBER_ENTRY = PlaceholderEntry(partFrame, placeholder="Enter Part Number", font=font)
      self.PART_NUMBER_ENTRY.grid(padx=4, pady=4, row=1, column=1)

      # part name section and placeholder widget
      part_name_label = Label(partFrame, text="Part Name:", font=font)
      part_name_label.grid(padx=4, row=1, column=2)
      self.PART_NAME_ENTRY = PlaceholderEntry(partFrame, placeholder="Enter Part Name", font=font)
      self.PART_NAME_ENTRY.grid(padx=4, row=1, column=3)

      # create frame to hold all of the check boxes to keep them organized
      checkBoxFrame = Frame(self.frame)
      checkBoxFrame.pack()

      # store all of the info to create the check boxes
      self.FOLDERS = [{
        'name': folder['name'],
        'defaultOn': folder['defaultOn'],
        'var': IntVar(checkBoxFrame, value=1)
      } for folder in self.__load_folders()]

      # store the location of the check boxes
      location = {'row': 0, 'column': 0}

      # create the check boxes
      for index, folder in enumerate(self.FOLDERS):
        cb = Checkbutton(checkBoxFrame, text=f"{folder['name']}", variable=folder['var'], font=font)
        folder['var'].set(folder['defaultOn'])
        if index % 3 == 0:
          location['row'] += 1
          location['column'] = 0
        else:
          location['column'] += 1
        cb.grid(padx=5, pady=5, row=location['row'], column=location['column'])

      # create the buttons on the bottom of the frame
      buttonFrame = Frame(self.frame)
      buttonFrame.pack()
      Button(buttonFrame,
             text="Set Path",
             command=self.__set_file,
             width=15,
             font=(None, 14)).grid(padx=5, row=0, column=0)
      Button(buttonFrame,
             text="Produce Folders",
             command=self.__create_folders,
             width=15,
             font=(None, 14)).grid(padx=5, row=0, column=1)
      Button(buttonFrame,
             text="Toggle All",
             command=self.__toggle_all,
             width=15,
             font=(None, 14)).grid(padx=5, row=0, column=2)

  def __load_folders(self):
    # load folders from json file
    folders = [folder for folder in self.data]
    # sort folders by name
    folders.sort(key=lambda x:x['name'])
    # return list of folders sorted by the name
    return folders

  def __create_file_path_label(self):
    # set file path label
    self.FILE_PATH_LABEL = Label(self.frame, text=f"Select Folder", font=(None, 16))
    self.FILE_PATH_LABEL.pack()

  def __create_folders(self):
    if self.FILE_PATH != "":
      # if we want to create the part folder also
      # even if checked will not work if either box is empty
      number = self.PART_NUMBER_ENTRY.grab_text()
      name = self.PART_NAME_ENTRY.grab_text()
      self.PART_NUMBER_ENTRY.grab_text()
      if name != "" and number != "":
          folder_name = "_".join([number, name])
          self.FILE_PATH = os.path.join(self.FILE_PATH,folder_name)
          if not os.path.exists(self.FILE_PATH):
            os.mkdir(self.FILE_PATH)
      # create all the folders in the list that is checked
      for folder in self.FOLDERS:
        if folder['var'].get() == 1:
          path = os.path.join(self.FILE_PATH, folder['name'])
          if not os.path.exists(path):
            print(f"Creating Folder: {path}")
            os.mkdir(path)
        # Open the folder in File Explorer.
      if self.CREATE_PART_FOLDER_VAR.get() == 1:
        if os.path.exists(self.FILE_PATH):
            # Determine the appropriate command based on the operating system
            if os.name == 'nt':  # Windows
                command = f'explorer "{os.path.realpath(self.FILE_PATH)}"'
            elif os.name == 'posix':  # Linux or macOS
                command = f'xdg-open "{os.path.realpath(self.FILE_PATH)}"'
            else:
                raise NotImplementedError(f'Unsupported operating system: {os.name}')
            
            # Open the folder path in the File Explorer
            subprocess.run(command, shell=True)
        else:
            print(f'Folder path does not exist: {self.FILE_PATH}')

  def __toggle_all(self):
    index = self.FOLDERS[0]['var'].get()
    if index == 0:
      index = 1
    else:
      index = 0
    for folder in self.FOLDERS:
      folder['var'].set(index)

  def __set_file(self):
    file_path = filedialog.askdirectory(
      title=f"{self.app.CURRENT_APP.value.title()} - Select Directory")
    if os.path.exists(file_path):
      self.FILE_PATH = file_path
      self.FILE_PATH_LABEL.config(text=f"{self.FILE_PATH}")
    else:
      self.FILE_PATH_LABEL.config(text="Invalid File Path")

class FormulaEntry (Entry):
  def __init__(self, master=None, rounding=4, *args, **kwargs):
    super ().__init__ (master, *args, **kwargs)
    self.rounding = rounding
    # Set the validation command to call the validate_number function
    self.validate_command = self.register (self.validate_number)
    self.config (validate="focusout", validatecommand=(self.validate_command, "%P"))

    # Internal variable to store the numeric value
    self.placeholder = 0.0
    self.value = self.placeholder

    self.bind ("<FocusIn>", self.on_entry_click)
    # Update the entry box with the initial formatted value
    self.__update_display ()

  def validate_number(self, new_value):
    # Check if the new value is a valid number
    try:
      # Remove commas from the new value (if any) to convert it back to a float
      float_value = float (new_value.replace (",", ""))
      self.value = float_value
      self.__update_display ()

      return True
    except ValueError:
      # Show an error message if the input is not a valid number
      self.bell ()
      return False

  def on_entry_click(self, event):
    if self.get_value() == 0.0:
        print(self.get_value())
        self.selection_range (0, 'end')

  def __update_display(self):
    # Format the numeric value with commas for readability
    formatted_value =  round(self.value, self.rounding)

    # Update the entry box with the formatted value
    self.delete (0, END)
    self.insert (0, f"{formatted_value:,}")

  def get_value(self):
    # Return the internal numeric value as a float
    return self.value

class Formulas(BaseApp):

  QUESTIONS = []
  ANSWER = None
  CURRENT_FORMULA = None
  ROUNDING = None

  
  def __init__(self, app, frame, data):
    super().__init__(app, frame, data)
    self.__load_formulas()

    # set file path label
    self.FILE_PATH_LABEL = Label(self.frame, text=f"Select Formula", font=(None, 16))
    self.FILE_PATH_LABEL.pack()

    # Create a StringVar to hold the selected formula
    self.selected_formula = StringVar(self.frame)
    self.selected_formula.set(self.FORMULAS[0]["name"])

    # setup drop down menu
    self.thread_menu = OptionMenu(self.frame, self.selected_formula, *[name["name"] for name in self.FORMULAS])
    self.thread_menu.config(font=(None, 15))
    self.thread_menu['menu'].config(font=('Courier', 15))
    self.thread_menu.pack(anchor="n")

    # Create a new LabelFrame
    self.question_frame = LabelFrame(self.frame, text="", font=(None, 18))
    self.question_frame.pack(padx=10, pady=10)

    # Create a trace to keep track of the option selected
    self.selected_formula.trace("w", self.__fill_in_questions)

    self.__fill_in_questions()

  def __load_formulas(self):
      # load formulas
      self.FORMULAS = [formula for formula in self.data]

  def __fill_in_questions(self, *args):
    for f in self.FORMULAS:
      if self.selected_formula.get() == f["name"]:
        self.CURRENT_FORMULA = f
        break
    self.__create_answer()
    self.__set_answer()
    self.ROUNDING = f['round']

    # clear existing variables
    for ques in self.QUESTIONS:
      ques['lbl'].destroy()
      ques["entry"].destroy()
    self.QUESTIONS.clear()

    idx = 0
    for index, i in enumerate(self.CURRENT_FORMULA["questions"]):
      ques = self.__create_question(i)
      ques["lbl"].grid(padx=5, pady=5, row=idx, column=0)
      ques["entry"].grid(padx=5, pady=5, row=idx, column=1)
      self.QUESTIONS.append(ques)
      idx += 1

    self.ANSWER["lbl"].grid(pady=5, row=idx, column=0)
    self.ANSWER["entry"].grid(pady=5, row=idx, column=1)
    self.app.reset_colors()

  def __create_question(self, name):
    label = Label(self.question_frame,
                  text=f"{name}:",
                  bg=self.app.COLOR_SCHEME.value['data_frame_background'],
                  fg=self.app.COLOR_SCHEME.value['data_frame_font'],
                  font=(None, 15))
    entry = FormulaEntry(self.question_frame, font=(None, 15))

    entry.bind("<FocusOut>", self.__solve_equaiton)
    entry.bind("<Return>", self.__solve_equaiton)
    return {"lbl": label, "entry": entry}

  def __create_answer(self):
    # Create Label and Entry for the Answer
    if self.ANSWER != None:
      self.ANSWER["lbl"].destroy()
      self.ANSWER["entry"].destroy()
    answer_label = Label(
      self.question_frame,
      text='answer',
      bg=self.app.COLOR_SCHEME.value['data_frame_background'],
      fg=self.app.COLOR_SCHEME.value['data_frame_font'],
      font=(None, 15))
    #answer_entry = Entry(self.question_frame, font=(None, 15))
    answer_entry = FormulaEntry(self.question_frame, rounding=self.ROUNDING, font=(None, 15))
    self.ANSWER = {'lbl': answer_label, "entry": answer_entry}

  def __solve_equaiton(self, args=''):
    solution = ''
    entry_data = []
    formula = None
    try:
      for q in self.QUESTIONS:
        entry = float(eval(q['entry'].get().replace(",", "")))
        try:
          q['var'].set(f"{entry:,}")
        except:
          pass
        entry_data.append(entry)
      formula = self.CURRENT_FORMULA["formula"]

    except:
      return

    for i in range(len(self.CURRENT_FORMULA['questions'])):
      formula = formula.replace(f"[{i}]", str(entry_data[i]))

    #print (f"Entry: {entry_data} | {formula}")
    try:
      solution = round(eval(formula), self.ROUNDING)
      # set answer entry to the solutioin
      self.__set_answer(solution)
    except:
      pass

  def __set_answer(self, answer=""):
    # set answer entry to the solutioin
    if self.CURRENT_FORMULA != None:
      self.ANSWER['lbl'].config(text=self.CURRENT_FORMULA['name'] + ":")
    try:
      answer = f"{answer:,}"
    except:
      pass
    self.ANSWER['entry'].config(state='normal')
    self.ANSWER['entry'].delete(0, END)
    self.ANSWER['entry'].insert(0, answer)
    self.ANSWER['entry'].config(state='readonly')

  def __format_number(self, *args):
    try:
      for ques in self.QUESTIONS:
        value_float = float(ques['var'].get())
        formatted_value = '{:,.0f}'.format(value_float)
        ques['var'].set(formatted_value)
    except:
      pass

class CodeVault(BaseApp):

  FILE_PATH = ""
  StoredCode = []

  def __init__(self, app, frame, data):
    super ().__init__ (app, frame, data)
    # load code data
    self.StoredCode = [file for file in self.data]
    self.StoredCode.sort(key=lambda x: x['name'])

    # store colors for off and even index in treeview
    self.colors = {'odd':'white', 'even': 'light gray'}

    # set file path label
    self.FILE_PATH_LABEL = Label(self.frame,
                                 text=f"Select Machine",
                                 font=(None, 16))
    self.FILE_PATH_LABEL.pack()

    # Create a StringVar to hold the selected machine
    self.selected_machine = StringVar(self.frame)
    self.selected_machine.set(self.StoredCode[0]['name'])

    # Create an OptionMenu of thread names
    self.thread_menu = OptionMenu(
      self.frame, self.selected_machine,
      *[file['name'] for file in self.StoredCode])
    self.thread_menu.config(font=(None, 15))
    self.thread_menu['menu'].config(font=(None, 15))
    self.thread_menu.pack(anchor="n")

    # Create an object of Style widget
    try:
      self.style = ttk.Style(self.frame)
      aktualTheme = self.style.theme_use()
      self.style.theme_create("dummy", parent=aktualTheme)
      self.style.theme_use("dummy")
      self.style.configure("Treeview.Heading", font=(None, 15))
      self.style.configure("Treeview", font=(None, 13))
    except:
      pass

    # create treeview
    self.tree = ttk.Treeview(self.frame, columns=("code", "description"))

    self.tree.heading('code', text="Code")
    self.tree.heading('description', text='Description')

    self.tree.column("code", width=100, anchor="center")
    self.tree.column("description", width=400, anchor="center")

    self.tree["show"] = "headings"

    # create the scrollbar and specify the Treeview as the parent
    scrollbar = Scrollbar(self.tree)

    # attach the scrollbar to the Treeview
    self.tree.config(yscrollcommand=scrollbar.set)

    # attach the Treeview to the scrollbar
    scrollbar.config(command=self.tree.yview)

    self.tree.pack(padx=20, pady=20, fill="both", expand=True)

    # place the scrollbar next to the Treeview
    scrollbar.place(relx=1.0, rely=0, relheight=1, relwidth=0.02)

    self.__load_data()

    self.selected_machine.trace("w", self.__load_data)

  def __load_data(self, *args):
    self.tree.delete(*self.tree.get_children())
    StoredCode = next(file for file in self.StoredCode
                        if file["name"] == self.selected_machine.get())
    for line in StoredCode['data']:
      self.tree.insert("", "end", values=(line["code"], line["description"]))
    self.treeview_sort_column("code", False)

    # Define the tag for even rows
    self.tree.tag_configure("even", background=self.colors['even'])
    self.tree.tag_configure("odd", background=self.colors['odd'])

    # Apply the tag to the appropriate rows
    for i in range(self.tree.get_children().__len__()):
      if i % 2 == 0:
        self.tree.item(self.tree.get_children()[i], tags="even")
      else:
        self.tree.item(self.tree.get_children()[i], tags="odd")

  def treeview_sort_column(self, col, reverse):
    l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
      self.tree.move(k, '', index)

class Cycle(Enum):

  HEADER = {'name':'HEADER'}
  PPM = {'name':'PPM'}
  SINGLE_PT = {'name':'SINGLE PT'}
  BORE_BOSS = {'name':'BORE / BOSS'}
  WEB_POCKET = {'name':'WEB / POCKET'}

class CycleEditor(Toplevel):
  def __init__(self, parent, cycle_data, index):
        super().__init__(parent)
        self.title("Cycle Editor")

        # stores index of item we are editing
        self.index = index
        
        self.cycle_data = cycle_data
        self.entry_vars = []

        self.__create_widgets()

  def __create_widgets(self):
        for label_text, entry_text in self.cycle_data.items():
            label = Label(self, text=label_text)
            label.pack()

            entry_var = StringVar()
            entry_var.set(entry_text)
            entry = Entry(self, textvariable=entry_var)
            entry.pack()

            self.entry_vars.append(entry_var)
        enter_button = Button(self, text="Enter", command=self.__on_enter)
        enter_button.pack()

  def __on_enter(self):
          new_data = {label_text: entry_var.get() for (label_text, _), entry_var in zip(self.cycle_data.items(), self.entry_vars)}
          self.master.update_cycle_data(new_data)
          self.destroy()

class ProbeBuilder(BaseApp):


  def __init__(self, app, frame, data):
    super ().__init__ (app, frame, data)
    # store colors for off and even index in treeview
    self.colors = {'odd':'white', 'even': 'light gray'}
    self.cycles = []
    # setup the frame    
    self.__setup__frames()
    self.__setup_buttons()
    self.__setup_treeview()
    self.__setup_right_click_menu()

    # Bind the right-click event to show the context menu
    self.tree.bind("<Button-3>", self.__show_context_menu)

  def __show_context_menu(self, event):
        # Get the item that was right-clicked
        item = self.tree.identify_row(event.y)
        if item:
            # Select the item
            self.tree.selection_set(item)
            # Display the context menu at the right-clicked position
            self.context_menu.post(event.x_root, event.y_root)

  def __edit_selected_item(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_index = self.tree.index(selected_item)
            # edit data grabbing index from cycles
            editor = CycleEditor(self.app.APP, self.cycles[item_index], item_index)

  def __remove_selected_item(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_index = self.tree.index(selected_item)
            self.cycles.remove(self.cycles[item_index])
        self.__load_info()

  def __setup_right_click_menu(self):
    # Create the right-click context menu
    self.context_menu = Menu(self.tree, tearoff=0)
    self.context_menu.add_command(label="Edit", command=self.__edit_selected_item)
    self.context_menu.add_command(label="Delete", command=self.__remove_selected_item)

  def __setup__frames(self):
    """
    creates the frame to hold everything and keep it visually nice
    """
    self.button_frame = Frame(self.frame)
    self.button_frame.pack(expand=False, padx=5, anchor=W)

    

  def __setup_buttons(self):
    buttons = [{'text':'HEADER', 'command':self.__add_header},
               {'text':'PPM', 'command':self.__add_ppm},
               {'text':'SINGLE PT', 'command':self.__add_single_pt},
               {'text':'BORE/BOSS', 'command':self.__add_bore_boss},
               {'text':'WEB/POCKET', 'command':self.__add_web_pocket}]
    for btn in buttons:
      Button(self.button_frame, text=btn['text'], command=btn['command']).pack(pady=5)

  def __setup_treeview(self):
    # create treeview
    self.tree = ttk.Treeview(self.frame, columns=("function"))
    self.tree.heading('function', text="Function")
    #self.tree.heading('edit', text='Edit')
    self.tree.column("function", anchor="center")
    #self.tree.column("edit", anchor="center")
    self.tree["show"] = "headings"
    self.tree.pack(padx=20, pady=20, fill="both", expand=False, anchor=E)

  def __load_info(self):
    self.tree.delete(*self.tree.get_children())
    for cycle in self.cycles:
      self.tree.insert("", "end", values=(cycle['name']))
    self.__update_tags()

  def __update_tags(self):
    # Define the tag for even rows
    self.tree.tag_configure("even", background=self.colors['even'])
    self.tree.tag_configure("odd", background=self.colors['odd'])
    # Apply the tag to the appropriate rows
    for i in range(self.tree.get_children().__len__()):
      if i % 2 == 0:
        self.tree.item(self.tree.get_children()[i], tags="even")
      else:
        self.tree.item(self.tree.get_children()[i], tags="odd")

  def update_cycle_data(self, new_data):
        self.cycles.append(new_data)
        print("Updated cycles:", self.cycles)

  def __add_header(self):
    # check if header is the 1st item, if not add it to the 1st item
    item = {'name': Cycle.HEADER.value, 'feed':'60'}
    for cycle in self.cycles:
      if cycle['name'] == Cycle.HEADER.value:
        return
    self.cycles.insert(0, item)
    self.__load_info()

  def __add_ppm(self):
    item = {'name': Cycle.PPM.value, 'feed':'60'}
    self.cycles.append(item)
    self.__load_info()

  def __add_single_pt(self):
    item = Cycle.SINGLE_PT.value
    self.cycles.append(item)
    self.__load_info()

  def __add_bore_boss(self):
    item = Cycle.BORE_BOSS.value
    self.cycles.append(item)
    self.__load_info()

  def __add_web_pocket(self):
    item = Cycle.WEB_POCKET.value
    self.cycles.append(item)
    self.__load_info() 

class JsonFileManager:
    def __init__(self):
        self.data = {}

    def load_json_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.data[file_path] = data
                return data
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode JSON in '{file_path}': {e}")
            return None

    def save_json_file(self, file_path, data):
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)
        except Exception as e:
            print(f"Error: Failed to save data to '{file_path}': {e}")

    def get_data(self, file_path):
        return self.data.get(file_path)


class JsonEditor(BaseApp):

  def __init__(self, app, frame, data):
    super().__init__(app, frame, data)
    self.StoredCode = [folder for folder in self.data]
    self.FILE_PATH = os.path.join(app.C_DRIVE, "folders.json")

    # add save button to save json data
    self.save_button = Button (self.frame, text="Save Data", font=(None, 12), command=self.save_json)
    self.save_button.pack (pady=5)

    # create text area
    self.textarea = Text (self.frame, wrap="word")
    self.textarea.pack (padx=8, pady=8, fill="both", expand=True)

    self.update_textarea()

  def save_json(self):
        if self.update_json_data():
          print("Saving json")
          self.app.JsonFileManager.save_json_file(self.FILE_PATH, data=self.JSON_DATA)
          self.save_button.config(text="File Saved")
        else:
          self.save_button.config(text="Error Not Saved")

  def update_textarea(self):
    self.textarea.delete (1.0, END)
    formatted_data = self.convert_json_to_single_line (self.data)
    self.textarea.insert (1.0, formatted_data)

  def convert_json_to_single_line(self, json_data):
    formatted_data = ""
    for item in json_data:
      name = item["name"]
      default_on = item["defaultOn"]
      line = f'Name: "{name}" On: "{default_on}"\n'
      formatted_data += line
    return formatted_data

  def update_json_data(self):
        try:
            edited_json = self.textarea.get(1.0, END)
            json_data = []
            lines = edited_json.split('\n')
            for line in lines:
                if line.strip():
                    name = line.split('Name: "')[1].split('" On: "')[0]
                    default_on = line.split('" On: "')[1].replace('"', '')
                    json_data.append({"name": name, "defaultOn": int(default_on)})
        except:
          return False
        self.JSON_DATA = json_data
        return True

class MessageCenter(BaseApp):

  def __init__(self, app, frame, data):
    super().__init__(app, frame, data)
    # SMTP settings
    self.SERVER ="smtp.office365.com"
    self.PORT = 587

    # email settings - junk email only for this, dont bother stealing my password 
    self.EMAIL = self.app.EMAIL_INFO

    # add save button to save json data
    self.send_button = Button (self.frame, text="Send Message", font=(None, 14), command=self.__send_message)
    self.send_button.pack (pady=5)

    # create text area
    self.textarea = Text (self.frame, wrap="word")
    self.textarea.pack (padx=12, pady=12, fill="both", expand=True)
    # Bind the Text widget to the text change event
    self.textarea.bind("<FocusIn>", self.on_text_change)

    # adds starting message to TextArea
    self.message = f"Welcome to the {self.app.CURRENT_APP.value.title()}\nShare your thoughts\n   - Report any Bugs\n   - Suggest Improvements\n   - Report any ideas you would like to see implemented\n"
    self.insert_text(self.message)

  def on_text_change(self, event):
    current_text = self.textarea.get(1.0, END).strip()

    if current_text == self.message.strip():
        self.textarea.tag_add("sel", 1.0, END)

  def alter_send_button_test(self, text):
    self.send_button.config(text=text)

  def reset_text_area(self):
    self.textarea.delete("1.0", END)

  def insert_text(self, text):
    self.reset_text_area()
    self.textarea.insert(END, text)

  def __send_message(self):
      # grabs the content inside the text area
      body = self.textarea.get(1.0, END)
      if (len(body) == 1) or (body.strip() in self.message.strip()):
            return
      self.alter_send_button_test("Sending Message")
      try:          
          # Set up the email message

          # get recipients
          recipients = []
          for mail in self.EMAIL['recipients']:
            recipients.append(mail[::-1].title())
            
          subject = f"CAM Assistant Automated Message from {os.getlogin()}"

          today = datetime.now()
          body_header = f"from {os.getlogin()} on {today.month}/{today.day}/{today.year}\n"
          # creates the email message
          email_message = f"From: {os.getlogin()}\nTo: {', '.join(recipients)}\nSubject: {subject}\n\n\nSender:\n{body_header}\nMessage:\n{body}"
        
          # Start the SMTP server and login
          # email data is reversed to make it harder for the info to be seen
          with smtplib.SMTP(self.SERVER, self.PORT) as server:
              server.starttls()
              server.login(self.EMAIL['email'][::-1].title(), self.EMAIL['password'][::-1].title())

              # Send the email
              server.sendmail(self.EMAIL['email'][::-1].title(), recipients, email_message)
          self.alter_send_button_test("Send Message")
          messagebox.showinfo("Email Sent", "Message sent, Thank you for your feed back.")
          self.reset_text_area()
      except Exception as e:
          messagebox.showerror(f"Error", f"Failed to send email.\n{e}")


class App:
  BUTTON_FRAME_BUTTONS = []
  LOGO_FRAME_LABELS = []
  DATA_FRAME_DATA = []


  APP_NAME = "CAM Assistant"
  SOURCE_PATH = None
  CURRENT_APP = None

  COLOR_SCHEMES = []
  SETTINGS = {}

  def __init__(self, app):
    # setup paths
    self.__setup_paths()

    # store instance of the app
    self.APP = app

    # set the geometry of the window
    self.APP.geometry("800x500")

    # setup the color schemes to the app
    self.__setup_color_scheme()

    # setup the Json File Manager
    self.JsonFileManager = JsonFileManager()

    # load standard settings
    self.__load_settings()
    self.__load_emial_settings()

    # load all of the json file data
    self.__load_json()    

    # create 3 frames to hold data
    self.__create_frames()

    # setup frames
    self.__setup_button_frame()
    self.__setup_logo_frame()
    self.__setup_home()
    self.__set_title()

    # set the function to run on shut down
    self.APP.protocol("WM_DELETE_WINDOW", self.__on_close)

    # Register the hotkey callback
    self.APP.bind('<KeyPress>', self.__key_press)

    # create a color scheme to the app, area to make different color schemes
    self.reset_colors()

    # tkinter main loop
    self.APP.mainloop()

  def __setup_paths(self):
    self.C_DRIVE = os.path.join("C:\\", "Users", os.getlogin(), "CamAssistant")
    self.CONFIG_PATH = os.path.join(self.C_DRIVE, "config.ini")
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    self.CONFIG_PATH = os.path.join(current_file_directory, self.CONFIG_PATH)
    


  def __setup_color_scheme(self):
    self.COLOR_SCHEMES = [scheme for scheme in ColorScheme]
    try:
      self.COLOR_SCHEME = ColorScheme[self.CONFIG.get('GENERAL', 'color_scheme')]
    except:
      self.COLOR_SCHEME = self.COLOR_SCHEMES[0]

  def __load_emial_settings(self):
    # Check if config file exists
    self.EMAIL_PATH = os.path.join(self.SOURCE_PATH, "data.ini")
    if os.path.isfile(self.EMAIL_PATH):
      # File exists, load it
      CONFIG = configparser.ConfigParser()
      CONFIG.read(self.EMAIL_PATH)
      # loads email address from file
      email = CONFIG.get("data", "email")
      #loads password from file
      password = CONFIG.get('data', 'password')
      # loads recipients from file, splits the names at spaces, data needs to be a list
      recipients = CONFIG.get('data', 'recipients').split(" ")
      # save email info to a dictionary for the message center to access this
      self.EMAIL_INFO = {'email':email, 'password': password, 'recipients':recipients}
    else:
      # Display the error message and close the app
      messagebox.showerror(f"Loading Failed", f"Failed to load emial config.\nClosing app.\n[ERROR]:{e}")
      self.APP.destroy()

  def __load_settings(self):
    # Check if config file exists
    if os.path.isfile(self.CONFIG_PATH):
      # File exists, load it
      self.CONFIG = configparser.ConfigParser()
      self.CONFIG.read(self.CONFIG_PATH)
      self.SOURCE_PATH = self.CONFIG.get("Paths", "source")
    else:
      # Display the error message and close the app
      messagebox.showerror(f"Loading Failed", f"Failed to load config.\nClosing app.\n[ERROR]:{e}")
      self.APP.destroy()


  def __load_json(self):
    try:
        self.JSON_THREADS = self.JsonFileManager.load_json_file(os.path.join(self.SOURCE_PATH, "threads.json"))
        self.JSON_CODE_VAULT = self.JsonFileManager.load_json_file(os.path.join(self.SOURCE_PATH, "code_vault.json"))
        self.JSON_FOLDERS = self.JsonFileManager.load_json_file(os.path.join(self.C_DRIVE, "folders.json"))
        self.JSON_FORMULAS = self.JsonFileManager.load_json_file(os.path.join(self.SOURCE_PATH, "formulas.json"))
        # print(json.dumps(self.JSON_FOLDERS, indent=2)) # for debugging json file
    except Exception as e:
      # Display the error message and close the app
      messagebox.showerror(f"Loading Failed", f"Failed to load data.\nClosing app.\n[ERROR]:{e}")
      self.APP.destroy()

  def __create_frames(self):
        self.LOGO_FRAME = Frame(self.APP, height=50)
        self.LOGO_FRAME.pack(side="bottom", fill="x")
        self.BUTTON_FRAME = Frame(self.APP, width=100)
        self.BUTTON_FRAME.pack(side="left", fill="y")
        self.DATA_frame = Frame(self.APP)
        self.DATA_frame.pack(side="right", fill="both", expand=True)

  def __key_press(self, event):
    #print(event.state, "----", event.keysym) # debugs keypressed and prints what the button is
    # right control button to edit folder defaults
    if event.keysym.lower() == "control_r":
      self.__edit_json()

  def reset_colors(self):
    self.APP.config(bg=self.COLOR_SCHEME.value['data_frame_background'])
    self.LOGO_FRAME.config(bg=self.COLOR_SCHEME.value["logo_frame_background"])
    self.BUTTON_FRAME.config(
      bg=self.COLOR_SCHEME.value["button_frame_background"])
    self.DATA_frame.config(bg=self.COLOR_SCHEME.value['data_frame_background'])
    for btn in self.BUTTON_FRAME_BUTTONS:
      btn.config(bg=self.COLOR_SCHEME.value['button_background'],
                 fg=self.COLOR_SCHEME.value["button_font"])
    for lbl in self.LOGO_FRAME_LABELS:
      lbl.config(bg=self.COLOR_SCHEME.value['logo_frame_background'],
                 fg=self.COLOR_SCHEME.value['logo_frame_font'])
    for widget in self.DATA_frame.winfo_children():
      # print(widget.widgetName) # to debug the name of the widget
      if widget.widgetName == "text":
            widget.config(bg=self.COLOR_SCHEME.value['message_background'], fg=self.COLOR_SCHEME.value['message_font']) 
      elif widget.widgetName == "frame":
        widget.config(bg=self.COLOR_SCHEME.value['data_frame_background'])
        for widg in widget.winfo_children():
          if widg.widgetName == "entry":
            if self.CURRENT_APP != Apps.FOLDERFACTORY:
              widg.config(
                bg=self.COLOR_SCHEME.value['data_frame_entry_background'],
                fg=self.COLOR_SCHEME.value['data_frame_entry_font'])           
          elif widg.widgetName == "checkbutton":
            widg.config(bg=self.COLOR_SCHEME.value['data_frame_background'],
                        fg=self.COLOR_SCHEME.value['checkbox_font'])
          elif widg.widgetName == "button":
            widg.config(
              bg=self.COLOR_SCHEME.value['data_frame_button_background'],
              fg=self.COLOR_SCHEME.value['data_frame_button_font'])
          else:
            widg.config(bg=self.COLOR_SCHEME.value['data_frame_background'],
                        fg=self.COLOR_SCHEME.value['data_frame_font'])
      elif widget.widgetName == "button":
        widget.config(
          bg=self.COLOR_SCHEME.value['data_frame_button_background'],
          fg=self.COLOR_SCHEME.value['data_frame_button_font'])

      else:
        if not widget.widgetName == "ttk::treeview":
          widget.config(bg=self.COLOR_SCHEME.value['data_frame_background'],
                        fg=self.COLOR_SCHEME.value['data_frame_font'])



  def __setup_button_frame(self):
    # creats all the buttons on the left hand side, follow format to add new buttons
    buttons = [{'text': Apps.HOME.value, 'command':self.__setup_home},
               {'text': Apps.THREADEXPERT.value, 'command': self.__setup_thread_helper},
               {'text': Apps.FORMULAWIZARD.value, 'command':self.__setup_formulas},
               {'text': Apps.FOLDERFACTORY.value , 'command':self.__setup_folders},
               {'text': Apps.CODEVAULT.value, 'command':self.__setup_code_database},
               {'text':Apps.PROBEBUILDER.value, 'command': self.__setup_probe_builder},
               {'text':Apps.MESSAGECENTER.value, 'command':self.__setup_message_center},
               {'text':f"{self.COLOR_SCHEME.name.upper()} MODE", 'command':self.__change_colors}               
               ]
    for index, button in enumerate(buttons):
      btn = Button(self.BUTTON_FRAME, text=button['text'], width=15, command=button['command'], font=(None, 10))
      btn.grid(padx=7, pady=10, row=index, column=0)
      self.BUTTON_FRAME_BUTTONS.append(btn)


  def __setup_logo_frame(self):
    lbl = Label(self.LOGO_FRAME, text=f"Powered by Winchester Automation", font=('Courier New', 10))
    lbl.pack()
    self.LOGO_FRAME_LABELS.append(lbl)

  def __setup_home(self):
    self.CURRENT_APP = Apps.HOME
    self.__reset_data_frame()
    self.__set_title()
    Home(self, self.DATA_frame, None)
    self.reset_colors()

  def __setup_thread_helper(self):
    self.CURRENT_APP = Apps.THREADEXPERT
    self.__reset_data_frame()
    self.__set_title()    
    ThreadExpert (self, self.DATA_frame, self.JSON_THREADS)
    self.reset_colors()

  def __setup_formulas(self):
    self.CURRENT_APP = Apps.FORMULAWIZARD
    self.__reset_data_frame()
    self.__set_title()
    Formulas(self, self.DATA_frame, self.JSON_FORMULAS)
    self.reset_colors()

  def __setup_folders(self):
    self.CURRENT_APP = Apps.FOLDERFACTORY
    self.__reset_data_frame()
    self.__set_title()
    self.__load_json()
    FolderFactory(self, self.DATA_frame, self.JSON_FOLDERS)
    self.reset_colors()

  def __setup_code_database(self):
    self.CURRENT_APP = Apps.CODEVAULT
    self.__reset_data_frame()
    self.__set_title()
    CodeVault (self, self.DATA_frame, self.JSON_CODE_VAULT)
    self.reset_colors()

  def __setup_probe_builder(self):
    self.CURRENT_APP = Apps.PROBEBUILDER
    self.__reset_data_frame()
    self.__set_title()
    ProbeBuilder(self, self.DATA_frame, None)
    self.reset_colors()

  def __setup_message_center(self):
    self.CURRENT_APP = Apps.MESSAGECENTER    
    self.__reset_data_frame()
    self.__set_title()
    MessageCenter(self, self.DATA_frame, None)
    self.reset_colors()
        

  def __edit_json(self):
    self.CURRENT_APP = Apps.JSONEDITOR
    self.__reset_data_frame()
    self.__set_title()    
    filename = self.JSON_FORMULAS
    JsonEditor(self, self.DATA_frame, self.JSON_FOLDERS)
    self.reset_colors()

  def __change_colors(self):
    for index in range(len(self.COLOR_SCHEMES)):
      if self.COLOR_SCHEMES[index] == self.COLOR_SCHEME:
        new_index = index + 1
        if new_index >= len(self.COLOR_SCHEMES):
          new_index = 0
        self.COLOR_SCHEME = self.COLOR_SCHEMES[new_index]
        break

    self.reset_colors()
    self.BUTTON_FRAME_BUTTONS[-1].config(
      text=f"{self.COLOR_SCHEME.name.upper()} MODE")

  def __reset_data_frame(self):
    for widget in self.DATA_frame.winfo_children():
      widget.destroy()
    self.DATA_FRAME_DATA.clear()

  def __set_title(self):
    title = ""
    if self.CURRENT_APP != Apps.HOME:
      title = f" - {self.CURRENT_APP.value}"
    self.APP.title(f"{self.APP_NAME} {title.title()}")

  def __on_close(self):
    # update stuff on close and resave data
    self.CONFIG.set("GENERAL", "color_scheme", self.COLOR_SCHEME.name)

    # save config file
    with open(self.CONFIG_PATH, 'w') as config_file:
      self.CONFIG.write(config_file)

    self.APP.destroy()

class Apps(Enum):
    """
    all of the sections of the apps name, come from here
    """
    HOME = "HOME"
    THREADEXPERT = "THREAD EXPERT"
    FORMULAWIZARD = "FORMULA WIZARD"
    FOLDERFACTORY = "FOLDER FACTORY"
    CODEVAULT = "CODE VAULT"
    JSONEDITOR  = "JSON EDITOR"
    PROBEBUILDER  = "PROBE BUILDER"
    MESSAGECENTER = "MESSAGE CENTER"

def main():
  root = Tk()
  App(root)

if __name__ == '__main__':
  main()
