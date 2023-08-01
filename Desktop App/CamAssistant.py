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
    "button_font": "black"
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
    "button_font": "black"
  }

class ThreadExpert:


  def __init__(self, frame, title, json_file):
    self.THREAD_DATA = [thread for thread in json_file]
    self.THREADS = [thread["size"] for thread in self.THREAD_DATA]
    self.DATA_FRAME = frame
    Label(self.DATA_FRAME, text=title, font=(None, 30)).pack()
    frame = Frame(self.DATA_FRAME)
    frame.pack()
    # keep the enter chamfer size as last in this list
    labels = [
      "Minor Diameter:", "Major Diameter:", "Threads / Inch (Pitch):", "Cutting Tap:", "Roll Tap:",
      "Breakout Chamfer:", "Contour Chamfer:", "Enter Chamfer:"
    ]
    self.ENTRIES = []
    btn_index = 0
    Label(frame, text="Select Threads:", font=(None, 14)).grid(row=0, column=0)
    self.SELECTED_THREAD = StringVar(frame)

    # create the the option menu and all the entry boxes
    self.SELECTED_THREAD.set(self.THREADS[0])
    optionMenu = OptionMenu(frame,
                            self.SELECTED_THREAD,
                            *self.THREADS,
                            command=self.__update_entries)
    optionMenu.config(font=(None, 15))
    optionMenu['menu'].config(font=(None, 15))
    optionMenu.grid(pady=5, row=0, column=1)

    for index, lbl in enumerate(labels, 1):
      Label(frame, text=lbl, font=(None, 14)).grid(pady=2, row=index, column=0)
      entry = Entry(frame, font=(None, 14))
      if index != len(labels):
        entry.configure(state='disabled')
        entry.bind("<KeyRelease>", self.__update_chamfers)
      entry.bind("<Return>", self.__bind_entries)
      #entry.trace ("w", self.__bind_entries)# ---------------------
      entry.grid(pady=2, row=index, column=1)
      self.ENTRIES.append(entry)
      btn_index += 1

    # setup enter button
    self.ENTER_BTN = Button(frame,
                            text="Calculate Chamfer",
                            command=self.__update_entries,
                            width=35,
                            font=(None, 14))
    self.ENTER_BTN.grid(pady=5, row=btn_index + 1, column=0, columnspan=2)
    self.__update_entries()

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

class FolderFactory:

  FILE_PATH = ''

  def __init__(self, frame, title, json_file, app):
    folders = [thread for thread in json_file]
    folders.sort(key=lambda x: x['name'])

    self.DATA_FRAME = frame
    self.APP = app
    self.TITLE = title
    Label(self.DATA_FRAME, text=title, font=(None, 30)).pack()

    # set file path label
    self.FILE_PATH_LABEL = Label(self.DATA_FRAME,
                                 text=f"Select Folder",
                                 font=(None, 16))
    self.FILE_PATH_LABEL.pack()

    partFrame = Frame(self.DATA_FRAME)
    partFrame.pack(padx=10)

    self.CREATE_PART_FOLDER_VAR = IntVar()
    self.CREATE_PART_FOLDER_VAR.set(1)
    create_folder_checkbox = Checkbutton(partFrame, text="Open Part Folder?", variable=self.CREATE_PART_FOLDER_VAR, font=(None, 16))
    create_folder_checkbox.grid(pady=5, row=0, columnspan=4)

    part_number_label = Label (partFrame, text="Part Number:", font=(None, 12))

    # part number section, label and placeholder widget
    part_number_label = Label(partFrame, text="Part Number:", font=(None, 12))
    part_number_label.grid(padx=4,pady=4, row=1, column=0)
    self.PART_NUMBER_ENTRY = PlaceholderEntry(partFrame, placeholder="Enter Part Number", font=(None, 12))
    self.PART_NUMBER_ENTRY.grid(padx=4, pady=4, row=1, column=1)

    # part name section and placeholder widget
    part_name_label = Label(partFrame, text="Part Name:", font=(None, 12))
    part_name_label.grid(padx=4, row=1, column=2)
    self.PART_NAME_ENTRY = PlaceholderEntry(partFrame, placeholder="Enter Part Name", font=(None, 12))
    self.PART_NAME_ENTRY.grid(padx=4, row=1, column=3)

    checkBoxFrame = Frame(self.DATA_FRAME)
    checkBoxFrame.pack()

    self.FOLDERS = [{
      'name': folder['name'],
      'defaultOn': folder['defaultOn'],
      'var': IntVar(checkBoxFrame, value=1)
    } for folder in folders]

    location = {'row': 0, 'column': 0}
    for index, folder in enumerate(self.FOLDERS):
      cb = Checkbutton(checkBoxFrame,
                       text=f"{folder['name']}",
                       variable=folder['var'],
                       font=(None, 12))
      folder['var'].set(
        folder['defaultOn'])  # set the initial state of the checkbox
      if index % 3 == 0:
        location['row'] += 1
        location['column'] = 0
      else:
        location['column'] += 1
      cb.grid(padx=5, pady=5, row=location['row'], column=location['column'])

    buttonFrame = Frame(self.DATA_FRAME)
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
      title=f"{self.TITLE.title()} - Select Directory")
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

class Formulas:

  QUESTIONS = []
  ANSWER = None
  CURRENT_FORMULA = None
  ROUNDING = None

  def __init__(self, frame, title, json_file, app):
    self.FORMULAS = [formula for formula in json_file]

    self.DATA_FRAME = frame
    self.APP = app
    Label(self.DATA_FRAME, text=title, font=(None, 30)).pack()

    # set file path label
    self.FILE_PATH_LABEL = Label(self.DATA_FRAME,
                                 text=f"Select Formula",
                                 font=(None, 16))
    self.FILE_PATH_LABEL.pack()

    # Create a StringVar to hold the selected formula
    self.selected_formula = StringVar(self.DATA_FRAME)
    self.selected_formula.set(self.FORMULAS[0]["name"])

    self.thread_menu = OptionMenu(self.DATA_FRAME, self.selected_formula,
                                  *[name["name"] for name in self.FORMULAS])
    self.thread_menu.config(font=(None, 15))
    self.thread_menu['menu'].config(font=('Courier', 15))
    self.thread_menu.pack(anchor="n")

    # Create a new LabelFrame
    self.question_frame = LabelFrame(self.DATA_FRAME, text="", font=(None, 18))
    self.question_frame.pack(padx=10, pady=10)

    # Create a trace to keep track of the option selected
    self.selected_formula.trace("w", self.__fill_in_questions)

    self.__fill_in_questions()

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
    self.APP.reset_colors()

  def __create_question(self, name):
    label = Label(self.question_frame,
                  text=f"{name}:",
                  bg=self.APP.COLOR_SCHEME.value['data_frame_background'],
                  fg=self.APP.COLOR_SCHEME.value['data_frame_font'],
                  font=(None, 15))
    #str_var = StringVar(self.DATA_FRAME)
    #str_var.set("0.")
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
      bg=self.APP.COLOR_SCHEME.value['data_frame_background'],
      fg=self.APP.COLOR_SCHEME.value['data_frame_font'],
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

class CodeVault:

  FILE_PATH = ""
  MACHINE_DATA = []

  def __init__(self, frame, title, json_file, app):
    self.MACHINE_DATA = [machine for machine in json_file]
    self.MACHINE_DATA.sort(key=lambda x: x['name'])

    self.DATA_FRAME = frame
    self.APP = app
    Label(self.DATA_FRAME, text=title, font=(None, 30)).pack()

    # set file path label
    self.FILE_PATH_LABEL = Label(self.DATA_FRAME,
                                 text=f"Select Machine",
                                 font=(None, 16))
    self.FILE_PATH_LABEL.pack()

    # Create a StringVar to hold the selected machine
    self.selected_machine = StringVar(self.DATA_FRAME)
    self.selected_machine.set(self.MACHINE_DATA[0]['name'])

    # Create an OptionMenu of thread names
    self.thread_menu = OptionMenu(
      self.DATA_FRAME, self.selected_machine,
      *[machine['name'] for machine in self.MACHINE_DATA])
    self.thread_menu.config(font=(None, 15))
    self.thread_menu['menu'].config(font=(None, 15))
    self.thread_menu.pack(anchor="n")

    # Create an object of Style widget
    try:
      self.style = ttk.Style(self.DATA_FRAME)
      aktualTheme = self.style.theme_use()
      self.style.theme_create("dummy", parent=aktualTheme)
      self.style.theme_use("dummy")
      self.style.configure("Treeview.Heading", font=(None, 15))
      self.style.configure("Treeview", font=(None, 13))
    except:
      pass

    # create treeview
    self.tree = ttk.Treeview(self.DATA_FRAME, columns=("code", "description"))

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

    self.tree.pack(padx=5, pady=5)

    # place the scrollbar next to the Treeview
    scrollbar.place(relx=1.0, rely=0, relheight=1, relwidth=0.02)

    self.__load_data()

    self.selected_machine.trace("w", self.__load_data)

  def __load_data(self, *args):
    self.tree.delete(*self.tree.get_children())
    machine_data = next(machine for machine in self.MACHINE_DATA
                        if machine["name"] == self.selected_machine.get())
    for line in machine_data['data']:
      self.tree.insert("", "end", values=(line["code"], line["description"]))
    self.treeview_sort_column("code", False)

    # Define the tag for even rows
    self.tree.tag_configure("even", background="gray")
    self.tree.tag_configure("odd", background="white")

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

class RotationMacro:

  QUESTIONS = []
  ANSWER = None
  CURRENT_FORMULA = None
  ROUNDING = 4

  def __init__(self, frame, title, json_file, app):
    self.MACHINE_DATA = [formula for formula in json_file]

    self.DATA_FRAME = frame
    self.APP = app
    Label(self.DATA_FRAME, text=title, font=(None, 30)).pack()

    # set machine label
    Label(self.DATA_FRAME, text=f"Select Machine", font=(None, 16)).pack()

    # Create a StringVar to hold the selected machine
    self.selected_machine_var = StringVar(self.DATA_FRAME)
    self.selected_machine_var.set(self.MACHINE_DATA[0]["name"])

    self.thread_menu = OptionMenu(
      self.DATA_FRAME, self.selected_machine_var,
      *[name["name"] for name in self.MACHINE_DATA])
    self.thread_menu.config(font=(None, 15))
    self.thread_menu['menu'].config(font=('Courier', 15))
    self.thread_menu.pack(anchor="n")

    # Create a new LabelFrame
    self.question_frame = LabelFrame(self.DATA_FRAME, text="", font=(None, 18))
    self.question_frame.pack(padx=10, pady=10)

    # setup labels for boxes
    Label(self.question_frame,
          text="WCS",
          font=(None, 15),
          bg=self.APP.COLOR_SCHEME.value['data_frame_background'],
          fg=self.APP.COLOR_SCHEME.value['data_frame_font']).grid(row=0,
                                                                  column=1)
    Label(self.question_frame,
          text="New WCS",
          font=(None, 15),
          bg=self.APP.COLOR_SCHEME.value['data_frame_background'],
          fg=self.APP.COLOR_SCHEME.value['data_frame_font']).grid(row=0,
                                                                  column=2)
    # setup entry boxes for answers
    self.ENTRY_BOXES = [{
      'name': "X Location", 'tag':'x pos'
    }, {
      'name': "Y Location", 'tag':'y pos'
    }, {
      'name': "Z Location", 'tag':'z pos'
    }, {
      'name': "Input Angle", 'tag':''
    }]
    for index, entry in enumerate(self.ENTRY_BOXES, 1):
      # setup labels
      entry['label'] = Label(self.question_frame,
                             text=entry['name'] + ":",
                             font=(None, 15))
      entry['label'].config(
        bg=self.APP.COLOR_SCHEME.value['data_frame_background'],
        fg=self.APP.COLOR_SCHEME.value['data_frame_font'])
      entry['label'].grid(padx=5, pady=5, row=index, column=0)
      # setup current wcs
      entry['wcs_var'] = StringVar(self.question_frame)
      #entry['wcs_var'].set('0')
      entry['wcs_entry'] = Entry(self.question_frame,
                                 textvariable=entry['wcs_var'],
                                 font=(None, 15))
      entry['wcs_entry'].bind("<FocusOut>", self.__solve_angle)
      entry['wcs_entry'].grid(padx=5, pady=5, row=index, column=1)
      # setup new positions
      entry['new_var'] = StringVar(self.question_frame)
      entry['new_var'].set('0')
      entry['new_entry'] = Entry(self.question_frame,
                                 textvariable=entry['new_var'],
                                 font=(None, 15))
      entry['new_entry'].bind("<FocusOut>", self.__solve_angle)
      entry['new_entry'].grid(padx=5, pady=5, row=index, column=2)

    # Create a trace to keep track of the option selected
    self.selected_machine_var.trace ("w", self.__solve_angle)

    self.__solve_angle ()

  def __solve_angle(self, *args):
    machine = next(
      (machine for machine in self.MACHINE_DATA if machine["name"] == self.selected_machine_var.get()), None)

    centerline = (machine['x pos'], machine['y pos'], machine['z pos'])

    try:
      userAngle = float(self.ENTRY_BOXES[-1]['new_entry'].get())
      position = [float(self.ENTRY_BOXES[0]['wcs_entry'].get()), float(self.ENTRY_BOXES[1]['wcs_entry'].get()),
                  float(self.ENTRY_BOXES[2]['wcs_entry'].get())]
      outputData = self.__calculate_position(position, centerline, userAngle)
    except:
      outputData = [m for m in machine]

    # sets the boxes if they have a tag
    for index, entry in enumerate(self.ENTRY_BOXES):
        if entry['tag'] != '':
          if entry['wcs_entry'].get() =="":
            self.__set_entry(entry['wcs_entry'], machine[entry['tag']], toLock=False)
          self.__set_entry(entry['new_entry'],outputData[index] )

  def __set_entry(self, entry, input, toLock=True):
    entry.config(state='normal')
    entry.delete(0, END)
    entry.insert(0, input)
    if toLock:
      entry.config(state='readonly')

  def __calculate_position(self,point, center, angle_y):
    # Convert angle to radians
    angle_y = -math.radians(angle_y)
    # Define rotation matrix around y axis
    R = [[math.cos(angle_y), 0, math.sin(angle_y)],
         [0, 1, 0],
         [-math.sin(angle_y), 0, math.cos(angle_y)]]
    # Subtract center from point
    point = [point[i] - center[i] for i in range(3)]
    # Apply rotation matrix
    point = [sum(R[i][j] * point[j] for j in range(3)) for i in range(3)]
    # Add center back to point
    point = [round(point[i] + center[i], self.ROUNDING) for i in range(3)]
    # Return rotated point
    return point

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

class Apps(Enum):
    HOME = "home"
    THREADEXPERT = "thread expert"
    FORMULAWIZARD = "formula wizard"
    FOLDERFACTORY = "folder factory"
    CODEVAULT = "code vault"
    JSONEDITOR  = "json editor"
    MESSAGECENTER = "message center"

class JsonEditor:

  def __init__(self, frame, title, json_file, app):
    self.MACHINE_DATA = [formula for formula in json_file]
    self.FILE_PATH = os.path.join(app.C_DRIVE, "folders.json")

    self.DATA_FRAME = frame
    self.APP = app
    self.JSON_DATA = json_file
    Label (self.DATA_FRAME, text=title, font=(None, 30)).pack (pady=5)
    # add save button to save json data
    self.save_button = Button (self.DATA_FRAME, text="Save Data", font=(None, 12), command=self.save_json)
    self.save_button.pack (pady=5)

    # create text area
    self.textarea = Text (self.DATA_FRAME, wrap="word")
    self.textarea.pack (padx=8, pady=8, fill="both", expand=True)



    self.update_textarea()

  def save_json(self):
        if self.update_json_data():
          print("Saving json")
          self.APP.JsonFileManager.save_json_file(self.FILE_PATH, data=self.JSON_DATA)
          self.save_button.config(text="File Saved")
        else:
          self.save_button.config(text="Error Not Saved")

  def update_textarea(self):
    self.textarea.delete (1.0, END)
    formatted_data = self.convert_json_to_single_line (self.JSON_DATA)
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

class MessageCenter:

  def __init__(self, frame, title, app):
    # SMTP settings
    self.SERVER ="smtp.office365.com"
    self.PORT = 587

    # email settings
    self.EMAIL = {"email":"CamAssistantAutomation@outlook.com", "password":"Password2444", "recipients":["WinchesterAutomation@outlook.com"]} 

    # app settings
    self.DATA_FRAME = frame
    self.APP = app
    Label (self.DATA_FRAME, text=title, font=(None, 30)).pack (pady=5)

    #Label (self.DATA_FRAME, text=message, font=(None, 12)).pack (pady=5)
    # add save button to save json data
    self.send_button = Button (self.DATA_FRAME, text="Send Email", font=(None, 14), command=self.__send_message)
    self.send_button.pack (pady=5)

    # create text area
    self.textarea = Text (self.DATA_FRAME, wrap="word")
    self.textarea.pack (padx=12, pady=12, fill="both", expand=True)
    # Bind the Text widget to the text change event
    self.textarea.bind("<FocusIn>", self.on_text_change)

    # adds starting message to TextArea
    self.message = f"Welcome to the {title.title()}\nShare your thoughts\n   - Report any Bugs\n   - Suggest Improvements\n   - Report any ideas you would like to see implemented\n"
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
    #self.reset_text_area()
    self.textarea.insert(END, text)

  def __send_message(self):
      # grabs the content inside the text area
      body = self.textarea.get(1.0, END)
      if (len(body) == 1) or (body.strip() in self.message.strip()):
            return
      self.alter_send_button_test("Sending Message")
      try:          
          # Set up the email message
          subject = f"Cam Assistant Automated Message from {os.getlogin()}"

          today = datetime.now()
          body_header = f"from {os.getlogin()} on {today.month}/{today.day}/{today.year}\n"
          # creates the email message
          email_message = f"From: {os.getlogin()}\nTo: {', '.join(self.EMAIL['recipients'])}\nSubject: {subject}\n\n\nSender:\n{body_header}\nMessage:\n{body}"
          # Start the SMTP server and login
          with smtplib.SMTP(self.SERVER, self.PORT) as server:
              server.starttls()
              server.login(self.EMAIL['email'], self.EMAIL['password'])

              # Send the email
              server.sendmail(self.EMAIL['email'], self.EMAIL['recipients'], email_message)
          self.alter_send_button_test("Send Message")
          messagebox.showinfo("Email Sent", "Message sent, Thank you for your feed back.")
      except Exception as e:
          messagebox.showerror(f"Error", f"Failed to send email.\n{e}")


class App:
  BUTTON_FRAME_BUTTONS = []
  LOGO_FRAME_LABELS = []
  DATA_FRAME_DATA = []

  C_DRIVE = os.path.join("C:\\", "Users", os.getlogin(), "CamAssistant")
  CONFIG_PATH = os.path.join(C_DRIVE, "config.ini")
  APP_NAME = "CAM ASSISTANT"
  SOURCE_PATH = None
  CURRENT_APP = None

  COLOR_SCHEMES = []
  SETTINGS = {}

  def __init__(self, app):
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    self.CONFIG_PATH = os.path.join(current_file_directory, self.CONFIG_PATH)
    self.APP = app
    self.APP.geometry("800x500")
    self.COLOR_SCHEMES = [scheme for scheme in ColorScheme]
    self.JsonFileManager = JsonFileManager()
    self.__load_settings()
    self.COLOR_SCHEME = ColorScheme[self.CONFIG.get('GENERAL', 'color_scheme')]

    # create 3 frames to hold data
    self.LOGO_FRAME = Frame(self.APP, height=50)
    self.LOGO_FRAME.pack(side="bottom", fill="x")
    self.BUTTON_FRAME = Frame(self.APP, width=100)
    self.BUTTON_FRAME.pack(side="left", fill="y")
    self.DATA_frame = Frame(self.APP)
    self.DATA_frame.pack(side="right", fill="both", expand=True)

    # setup frames
    self.__setup_button_frame()
    self.__setup_logo_frame()
    self.__setup_home()
    self.__set_title()

    self.APP.protocol("WM_DELETE_WINDOW", self.__on_close)

    # Register the hotkey callback
    self.APP.bind('<KeyPress>', self.__key_press)

    # create a color scheme to the app, area to make different color schemes
    self.reset_colors()
    self.APP.mainloop()

  def __load_settings(self):
    # Check if config file exists
    if os.path.isfile(self.CONFIG_PATH):
      # File exists, load it
      self.CONFIG = configparser.ConfigParser()
      self.CONFIG.read(self.CONFIG_PATH)
      self.SOURCE_PATH = self.CONFIG.get("Paths", "source")
    else:
      # File doesn't exist, create it
      self.CONFIG = configparser.ConfigParser()
      # Add your default settings or leave it empty
      self.CONFIG['GENERAL'] = {"color_scheme":"DARK","version":"-1"}
      self.CONFIG['Paths'] = {"source": "C:\\Users\\dwinc\\Desktop\\Setup Folder"}
      with open(self.CONFIG_PATH, 'w') as config_file:
        self.CONFIG.write(config_file)

    # loads json data
    self.__load_json()

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

  def __key_press(self, event):
    #print(event.state, "----", event.keysym)
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
      if widget.widgetName == "frame":
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
    buttons = [{'text':'HOME', 'command':self.__setup_home},
               {'text':'THREAD EXPERT', 'command': self.__setup_thread_helper},
               {'text':'FORMULA WIZARD', 'command':self.__setup_formulas},
               {'text':'FOLDER FACTORY', 'command':self.__setup_folders},
               {'text':'CODE VAULT', 'command':self.__setup_code_database},
               {'text':'MESSAGE CENTER', 'command':self.__setup_message_center},
               {'text':f"{self.COLOR_SCHEME.name.upper()} MODE", 'command':self.__change_colors}
               ]
    for index, button in enumerate(buttons):
      btn = Button(self.BUTTON_FRAME, text=button['text'], width=15, command=button['command'], font=("Georgia", 10))
      btn.grid(padx=7, pady=10, row=index, column=0)
      self.BUTTON_FRAME_BUTTONS.append(btn)


  def __setup_logo_frame(self):
    lbl = Label(self.LOGO_FRAME,
                text=f"Powered by Winchester Automation",
                font=('Courier New', 10))
    lbl.pack()
    self.LOGO_FRAME_LABELS.append(lbl)

  def __setup_home(self):
    self.__reset_data_frame()
    self.__set_title()
    self.CURRENT_APP = Apps.HOME
    lbl = Label(self.DATA_frame,
                text=f"Welcome to {self.APP_NAME.title()}!",
                font=(None, 30))
    lbl.pack(expand=True, anchor='center')
    self.reset_colors()

  def __setup_thread_helper(self, name="THREAD EXPERT"):
    self.__reset_data_frame()
    self.__set_title(f" - {name}")
    self.CURRENT_APP = Apps.THREADEXPERT
    ThreadExpert (self.DATA_frame, name, self.JSON_THREADS)
    self.reset_colors()

  def __setup_formulas(self, name="FORMULA WIZARD"):
    self.__reset_data_frame()
    self.__set_title(f" - {name}")
    self.CURRENT_APP = Apps.FORMULAWIZARD
    Formulas(self.DATA_frame,
             title=name,
             json_file=self.JSON_FORMULAS,
             app=self)
    self.reset_colors()

  def __setup_folders(self, name="FOLDER FACTORY"):
    self.__reset_data_frame()
    self.__set_title(f" - {name}")
    self.__load_json()
    self.CURRENT_APP = Apps.FOLDERFACTORY
    FolderFactory(self.DATA_frame,
              title=name,
              json_file=self.JSON_FOLDERS,
              app=self.APP)
    self.reset_colors()

  def __setup_code_database(self, name="CODE VAULT"):
    self.__reset_data_frame()
    self.__set_title(f" - {name}")
    self.CURRENT_APP = Apps.CODEVAULT
    CodeVault(self.DATA_frame,
                 title=name,
                 json_file=self.JSON_CODE_VAULT,
                 app=self.APP)
    self.reset_colors()

  def __setup_message_center(self, name="MESSAGE CENTER"):
    self.__reset_data_frame()
    self.__set_title(f" - {name}")
    self.CURRENT_APP = Apps.MESSAGECENTER
    MessageCenter(self.DATA_frame,
                 title=name,
                 app=self.APP)
    self.reset_colors()
    
    

  def __edit_json(self):
    name = "Folder Factory Editor"
    self.__reset_data_frame()
    self.__set_title(f" - {name}")
    self.CURRENT_APP = Apps.JSONEDITOR
    filename = self.JSON_FORMULAS
    JsonEditor(self.DATA_frame,
                 title=name,
                 json_file=self.JSON_FOLDERS,
                 app=self)
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

  def __set_title(self, page=""):
    self.APP.title(f"{self.APP_NAME.title()} {page.title()}")

  def __on_close(self):
    # update stuff on close and resave data
    self.CONFIG.set("GENERAL", "color_scheme", self.COLOR_SCHEME.name)

    # save config file
    with open(self.CONFIG_PATH, 'w') as config_file:
      self.CONFIG.write(config_file)

    self.APP.destroy()

def main():
  root = Tk()
  App(root)

if __name__ == '__main__':
  main()
