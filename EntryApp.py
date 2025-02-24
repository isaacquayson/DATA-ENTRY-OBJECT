import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import numpy as np
import threading
from tkcalendar import DateEntry
from mysql.connector import pooling

# Connection Pooling
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=20,
    host="localhost",
    user="root",
    password="Isaac%quayson2580",
    database="gds_database"
)


# Function to get a connection from the pool
def get_connection():
    return connection_pool.get_connection()


# Database connection function
def connect_to_db():
    try:
        return get_connection()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to connect to database: {err}")
        return None


# Function to populate the Treeview based on selected table (with optional filtering)
def load_table_data(table_name, columns, filter_column=None, filter_value=None):
    db = connect_to_db()
    if not db:
        return

    # Clear previous entries in the Treeview
    tree.delete(*tree.get_children())

    # Update the treeview columns dynamically
    clean_columns = [col.lstrip('\ufeff') for col in columns]  # Remove BOM from column names
    tree["columns"] = clean_columns
    for col in clean_columns:
        tree.heading(col, text=col, anchor="center")  # Set header text
        tree.column(col, width=50, anchor="center")  # Center align the column values

    try:
        cursor = db.cursor()
        if filter_column and filter_value:
            query = f"SELECT * FROM {table_name} WHERE {filter_column} = %s"
            cursor.execute(query, (filter_value,))
        else:
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)

        rows = cursor.fetchall()
        if rows:
            for row in rows:
                tree.insert("", "end", values=row)
        else:
            pass
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error retrieving data: {err}")
    finally:
        db.close()


def load_data_in_thread(table_name, columns, filter_column=None, filter_value=None):
    thread = threading.Thread(target=load_table_data, args=(table_name, columns, filter_column, filter_value))
    thread.start()


def on_table_select(event):
    try:
        # Check if there is a valid selection before getting the table name
        if table_listbox.curselection():
            selected_table = table_listbox.get(table_listbox.curselection())
        else:
            return  # Exit if no table is selected
    except tk.TclError:
        return  # Exit if an error occurs while selecting the table

    # Hide all current entry fields
    hide_entries()

    # Define table configurations for different tables
    table_config = {
        "samples": (samples_entries, samples_entries_labels, submit_samples_data),
        "survey": (survey_entries, survey_entries_labels, submit_survey_data),
        "Project_Table": (Project_Table_entries, Project_Table_entries_labels, submit_Project_Table_data),
        "collar": (collar_entries, collar_entries_labels, submit_collar_data),
        "lithology": (lithology_entries, lithology_entries_labels, submit_lithology_data),
        "alteration": (alteration_entries, alteration_entries_labels, submit_alteration_data),
        "assay": (assay_entries, assay_entries_labels, submit_assay_data),
        "sample_type": (sample_type_entries, sample_type_entries_labels, submit_sample_type_data)
    }

    # Check if the selected table has a configuration
    if selected_table in table_config:
        # Get the relevant entry fields, labels, and submit function
        entries, labels, submit_func = table_config[selected_table]

        # Show entry fields for the selected table
        show_entries(entries, labels)

        # Load data into the treeview for the selected table
        load_table_data(selected_table, labels)

        # Configure the submit button to use the correct submit function
        submit_button.config(command=submit_func)

        # Populate the first dropdown with column names for filtering
        column_dropdown['menu'].delete(0, 'end')
        for col in labels:
            clean_col = col.lstrip('\ufeff')
            column_dropdown['menu'].add_command(label=clean_col, command=tk._setit(selected_column, clean_col))
        selected_column.set('Select Column')  # Reset column dropdown to default

        # Special handling for the "samples" table
        if selected_table == "samples":
            # Populate the DataSet combobox with codes from the sample_type table
            populate_samples_dataset_combobox()

        if selected_table == "samples":
            # Populate the DataSet combobox with codes from the DataSet_Table
            populate_dataset_combobox1()

        # Special handling for the "collar" table
        if selected_table == "collar":
            # Populate the DataSet combobox with codes from the DataSet_Table
            populate_dataset_combobox()

        if selected_table == "survey":
            # Populate the DataSet combobox with codes from the DataSet_Table
            populate_dataset_combobox1()

        if selected_table == "assay":
            # Populate the DataSet combobox with codes from the DataSet_Table
            populate_dataset_combobox1()

        if selected_table == "alteration":
            # Populate the DataSet combobox with codes from the DataSet_Table
            populate_dataset_combobox1()

        if selected_table == "lithology":
            # Populate the DataSet combobox with codes from the DataSet_Table
            populate_dataset_combobox1()

        if selected_table == "alteration":
            # Populate the DataSet combobox with codes from the collar hole id
            populate_dataset_combobox2()

        if selected_table == "lithology":
            # Populate the DataSet combobox with codes from the collar hole id
            populate_dataset_combobox2()

        if selected_table == "survey":
            # Populate the DataSet combobox with codes from the collar
            populate_dataset_combobox2()

        if selected_table == "samples":
            # Populate the DataSet combobox with codes from the DataSet_Table
            populate_dataset_combobox2()


def populate_unique_values(*args):
    # Get the selected table and column
    if table_listbox.curselection():
        selected_table = table_listbox.get(table_listbox.curselection())
    else:
        messagebox.showerror("Error", "No table selected.")
        return

    column = selected_column.get()

    # Ensure the user doesn't select the default 'Select Column'
    if column == 'Select Column':
        return

    db = connect_to_db()
    if not db:
        return

    try:
        cursor = db.cursor()

        # Fetch unique values from the selected column in the selected table
        query = f"SELECT DISTINCT `{column}` FROM `{selected_table}`"
        cursor.execute(query)
        unique_values = [row[0] for row in cursor.fetchall()]

        # Clear the Listbox and populate it with the fetched unique values
        selected_value_listbox.delete(0, tk.END)
        for value in unique_values:
            selected_value_listbox.insert(tk.END, value)

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error fetching unique values: {err}")
    finally:
        db.close()


table_columns = {
    "samples": ["DataSet", "SampleID", "Sample_Type", "Hole_ID", "Depth_From", "Depth_To", "Interval_Length"],
    "survey": ["DataSet", "Hole_ID", "Depth", "Survey_Method", "Dip", "Orig_Azimuth"],
    "Project_Table": ['Code', 'Name', 'Description'],
    "sample_type": ['Code', 'Name', 'Description'],
    "lithology": ['DataSet', 'Hole_ID', 'Depth_From', 'Depth_To','Interval_Length', 'Lith1_Code'],
    "alteration": ['DataSet', 'Hole_ID', 'Depth_From', 'Depth_To', 'Interval_Length', 'Alt1_Code'],
    "assay": ['DataSet', 'SampleID', 'GenericMethod', 'LabElement', 'UnitCode', 'AssayResultNum'],
    "collar": ['DataSet', 'Hole_Type', 'Hole_ID', 'Max_Depth', 'Date', 'Orig_East', 'Orig_North', 'Orig_RL']
}


def filter_data():
    selected_table = table_listbox.get(table_listbox.curselection()[0])
    selected_values = [selected_value_listbox.get(i) for i in selected_value_listbox.curselection()]

    if not selected_values:
        messagebox.showwarning("No selection", "Please select one or more values to filter.")
        return

    column_to_filter = selected_column.get()

    # Ensure that column_to_filter is a valid column name
    if column_to_filter not in table_columns[selected_table]:
        messagebox.showerror("Error", f"Invalid column name: {column_to_filter}")
        return

    filter_query = f"SELECT * FROM {selected_table} WHERE {column_to_filter} IN ({', '.join(['%s'] * len(selected_values))})"

    db = connect_to_db()
    if not db:
        return

    try:
        cursor = db.cursor()
        cursor.execute(filter_query, selected_values)
        results = cursor.fetchall()

        # Clear the Treeview and populate it with the filtered results
        tree.delete(*tree.get_children())
        for row in results:
            tree.insert("", "end", values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to filter data: {err}")
    finally:
        db.close()


# Generic function to show entry fields
def show_entries(entries_dict, labels):
    global current_entries
    current_entries = entries_dict  # Set the current active entries
    for i, label in enumerate(labels):
        entry = entries_dict[label]  # Fetch the corresponding entry widget from the dictionary
        tk.Label(input_frame, text=label.lstrip('\ufeff'), bg='white', font=('Times New Roman', 12)).grid(row=i,
                                                                                                          column=0,
                                                                                                          padx=10,
                                                                                                          pady=5)
        entry.grid(row=i, column=1, padx=20, pady=5)


def submit_samples_data():
    submit_data_to_db("samples", samples_entries, samples_entries_labels)


def submit_survey_data():
    submit_data_to_db("survey", survey_entries, survey_entries_labels)


def submit_Project_Table_data():
    submit_data_to_db("Project_Table", Project_Table_entries, Project_Table_entries_labels)


def submit_collar_data():
    submit_data_to_db("collar", collar_entries, collar_entries_labels)


def submit_lithology_data():
    submit_data_to_db("lithology", lithology_entries, lithology_entries_labels)


def submit_alteration_data():
    submit_data_to_db("alteration", alteration_entries, alteration_entries_labels)


def submit_assay_data():
    submit_data_to_db("assay", assay_entries, assay_entries_labels)


def submit_sample_type_data():
    submit_data_to_db("sample_type", sample_type_entries, sample_type_entries_labels)


def submit_data_to_db(table_name, entries_dict, labels):
    db = connect_to_db()
    if not db:
        return

    # Collect values, replacing empty entries with None (for NULL in the database)
    values = [entries_dict[label].get() if entries_dict[label].get() != "" else None for label in labels]

    try:
        cursor = db.cursor()
        placeholders = ", ".join(["%s"] * len(values))
        columns = ", ".join(labels)
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        db.commit()

        messagebox.showinfo('success', "Data inserted successfully")
        tree.insert("", "end", values=values)  # Add the submitted data to the Treeview

        # Clear the entries if data was submitted successfully
        clear_entries()

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to insert data: {err}")
    finally:
        db.close()


# Function to clear entry fields
def clear_entries():
    if current_entries:
        for entry in current_entries.values():
            entry.delete(0, tk.END)  # Clear the content of the entry fields


# Function to hide entry fields
def hide_entries():
    for widget in input_frame.winfo_children():
        widget.grid_forget()  # Hide all widgets in the input frame


# Initialize the current entries variable
current_entries = None

# Creating the app window
root = tk.Tk()
root.title("DATA ENTRY OBJECT")
root.geometry("1300x700")


# Create a PanedWindow for interactive table selection
paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=15, bg='gold')
paned_window.place(relx=0.5, rely=1 / 3, anchor='center')  # Positioned to 1/3 from the top of the screen

# Create a frame for the left table list
table_frame = tk.Frame(paned_window, bg='gold4')
paned_window.add(table_frame, width=100)  # Adjust width for medium size

# Listbox for tables
table_listbox = tk.Listbox(table_frame, font=('Times New Roman', 12), bg='ivory3', height=8, width=20)
table_listbox.pack(fill=tk.BOTH, expand=True)

# Populate Listbox with table names
tables = np.array(['Project_Table',  'collar', 'sample_type', "samples",'survey', 'assay', 'lithology', 'alteration'])
for table in tables:
    table_listbox.insert(tk.END, table)

# Bind selection event
table_listbox.bind('<<ListboxSelect>>', on_table_select)

# Create a frame for the input fields
input_frame = tk.Frame(paned_window, bg='deep sky blue', bd=0, width=600, height=460)
paned_window.add(input_frame)

# Allow resizing of the panes dynamically
paned_window.paneconfig(input_frame, stretch="always")


# class for the tooltip message
class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tooltip_window = None

    def show_tooltip(self, text):
        if self.tooltip_window or not text:
            return

        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Removes the window decorations
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=text, background="plum1", relief="solid", borderwidth=1)
        label.pack(ipadx=1)

    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def populate_dataset_combobox():
    db = connect_to_db()
    if not db:
        return

    try:
        cursor = db.cursor()
        cursor.execute("SELECT Code, Name, Description FROM Project_Table")
        datasets = cursor.fetchall()  # Fetch all datasets

        codes = [row[0] for row in datasets]  # Extract codes for the dropdown
        collar_entries['DataSet']['values'] = codes

        # Create a dictionary for tooltips
        dataset_tooltips = {row[0]: f"Name: {row[1]}\nDescription: {row[2]}" for row in datasets}

        # Create a ToolTip instance
        tooltip = ToolTip(collar_entries['DataSet'])

        # Define function to show tooltip
        def on_hover(event):
            current_value = collar_entries['DataSet'].get()
            if current_value in dataset_tooltips:
                tooltip.show_tooltip(dataset_tooltips[current_value])

        # Define function to hide tooltip
        def on_leave(event):
            tooltip.hide_tooltip()

        # Bind events to the combobox
        collar_entries['DataSet'].bind("<Enter>", on_hover)  # Mouse enters
        collar_entries['DataSet'].bind("<Leave>", on_leave)  # Mouse leaves

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error fetching DataSet codes: {err}")
    finally:
        db.close()


def populate_dataset_combobox2():
    db = connect_to_db()
    if not db:
        return

    try:
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT Hole_ID FROM collar")
        codes2 = [row[0] for row in cursor.fetchall()]

        # Update the 'Hole_ID' combobox for both the 'collar' and 'survey' tables
        update_combobox(survey_entries['Hole_ID'], codes2)
        update_combobox(samples_entries['Hole_ID'], codes2)
        update_combobox(alteration_entries['Hole_ID'], codes2)
        update_combobox(lithology_entries['Hole_ID'], codes2)

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error fetching Hole_ID codes: {err}")
    finally:
        db.close()


def update_combobox(combobox, values):
    """Updates combobox values and sets it to editable."""
    combobox['values'] = values
    combobox.set('')  # Optional: clear previous selection
    combobox.config(state='normal')  # Make editable

    # Bind the event to filter values
    combobox.bind('<KeyRelease>', lambda event: filter_combobox(combobox, values))


def filter_combobox(combobox, all_values):
    """Filters the combobox based on user input."""
    typed_value = combobox.get()

    # Find matching values
    matched_values = [value for value in all_values if typed_value.lower() in value.lower()]

    # Update the combobox values based on matches
    if matched_values:
        combobox['values'] = matched_values  # Show matched values
    else:
        combobox['values'] = []  # Clear the dropdown values if no matches


def populate_dataset_combobox1():
    db = connect_to_db()
    if not db:
        return

    try:
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT DataSet FROM collar")
        codes1 = [row[0] for row in cursor.fetchall()]

        # Update the 'DataSet' combobox for both the 'collar' and 'survey' tables

        if 'DataSet' in survey_entries:
            survey_entries['DataSet']['values'] = codes1
        if 'DataSet' in assay_entries:
            assay_entries['DataSet']['values'] = codes1
        if 'DataSet' in alteration_entries:
            alteration_entries['DataSet']['values'] = codes1
        if 'DataSet' in lithology_entries:
            lithology_entries['DataSet']['values'] = codes1
        if 'DataSet' in samples_entries:
            samples_entries['DataSet']['values'] = codes1

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error fetching DataSet codes: {err}")
    finally:
        db.close()


def populate_samples_dataset_combobox():
    db = connect_to_db()
    if not db:
        return

    try:
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT Code FROM sample_type")
        codes = [row[0] for row in cursor.fetchall()]

        # Set the options in the DataSet combobox for the samples table
        samples_entries['Sample_Type']['values'] = codes

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error fetching DataSet codes from sample_type: {err}")
    finally:
        db.close()


# DataSet_Table entry fields
Project_Table_entries_labels = np.array(['Code', 'Name', 'Description'])
Project_Table_entries = {label: tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white')
                   for label in Project_Table_entries_labels}

# sample_type entry fields
sample_type_entries_labels = np.array(['Code', 'Name', 'Description'])
sample_type_entries = {label: tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white')
                  for label in sample_type_entries_labels}


# Samples entry fields
samples_entries_labels = np.array(['DataSet', 'SampleID', 'Sample_Type', 'Hole_ID', 'Depth_From', 'Depth_To', 'Interval_Length'])
samples_entries = {
    'DataSet': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=28, state='readonly'),
    'SampleID': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Sample_Type': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=30, state = 'readonly'),
    'Hole_ID': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=28, state='normal'),
    'Depth_From': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Depth_To': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Interval_Length': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white')

}

# Survey entry fields
survey_entries_labels = np.array(['DataSet', 'Hole_ID', 'Depth', 'Survey_Method', 'Dip',"Orig_Azimuth"])
survey_entries ={
    'DataSet': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=28, state='readonly'),  # Change to Combobox
    'Hole_ID': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=28, state='normal'),
    'Depth': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Survey_Method': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Dip': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    "Orig_Azimuth" : tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white')
}

# lithology entry fields
lithology_entries_labels = np.array(['DataSet', 'Hole_ID', 'Depth_From', 'Depth_To','Interval_Length', 'Lith1_Code'])
lithology_entries = {
    'DataSet': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=28, state='readonly'),
    'Hole_ID': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=28, state='normal'),
    'Depth_From': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Depth_To': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Interval_Length': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Lith1_Code': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white')
}


# alteration entry fields
alteration_entries_labels = np.array(['DataSet', 'Hole_ID', 'Depth_From', 'Depth_To', 'Interval_Length', 'Alt1_Code'])
alteration_entries = {
    'DataSet': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=28, state='readonly'),
    'Hole_ID': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=28, state='normal'),
    'Depth_From': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Depth_To': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Interval_Length': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Alt1_Code': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white')
}

# assay entry fields
assay_entries_labels = np.array(['DataSet', 'SampleID', 'GenericMethod', 'LabElement', 'UnitCode', 'AssayResultNum'])
assay_entries = {
    'DataSet': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=28, state='readonly'),
    'SampleID': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'GenericMethod': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'LabElement': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'UnitCode': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'AssayResultNum': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white')
}


# collar entry fields
collar_entries_labels = np.array(['DataSet', 'Hole_Type', 'Hole_ID', 'Max_Depth', 'Date', 'Orig_East', 'Orig_North', 'Orig_RL'])
collar_entries = {
    'DataSet': ttk.Combobox(input_frame, font=('Times New Roman', 12), width=28, state='readonly'),
    'Hole_Type': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Hole_ID': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Max_Depth': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Date': DateEntry(input_frame, font=('Times New Roman', 12), width=30, bg='orange', date_pattern='yyyy-mm-dd', state='readonly'),
    'Orig_East': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Orig_North': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white'),
    'Orig_RL': tk.Entry(input_frame, font=('Times New Roman', 12), width=30, bg='white')

}

# Dropdowns for filtering
filter_frame = tk.Frame(paned_window, bg='light green', bd=2, width=260)  # Set width to 800 pixels
filter_frame.pack(fill=tk.BOTH, expand=True)  # Ensure the frame fills the x-axis and expands
paned_window.add(filter_frame)

# Allow resizing of the panes dynamically
paned_window.paneconfig(filter_frame, stretch="always")

# Dropdown for selecting column
selected_column = tk.StringVar()
selected_column.set('Select Column')
column_dropdown = tk.OptionMenu(filter_frame, selected_column, 'Select Column')
column_dropdown.pack(pady=10)

selected_column.trace('w', populate_unique_values)

# Create a scrollable Listbox for selecting unique values
listbox_frame = tk.Frame(filter_frame)
listbox_frame.pack(pady=10, fill=tk.BOTH, expand=True)

# Create a scrollable Listbox for selecting unique values
selected_value_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, height=6, exportselection=False)
selected_value_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a search entry and button
search_entry = tk.Entry(filter_frame, font=('Times New Roman', 12))
search_entry.pack(pady=10)


# Create a frame to center the Select All button
select_all_frame = tk.Frame(listbox_frame)
select_all_frame.pack(side=tk.TOP)

# Add a "Select All" button to the centered frame
select_all_button = tk.Button(select_all_frame, text="Select All", command=lambda: select_all_items(), bg='lightblue', fg='black', font=('Times New Roman', 10, 'bold'))
select_all_button.pack(pady=(0, 5))


def select_all_items():
    """Toggle select all items in the Listbox."""
    current_selection = selected_value_listbox.curselection()
    if len(current_selection) == selected_value_listbox.size():
        # If all items are selected, deselect all
        selected_value_listbox.selection_clear(0, tk.END)
    else:
        # Select all items
        selected_value_listbox.selection_set(0, tk.END)


def filter_listbox():
    search_term = search_entry.get().lower()
    all_items = selected_value_listbox.get(0, tk.END)

    # Find matching items based on the search term
    matched_items = [item for item in all_items if search_term in item.lower()]

    # If no items match, show an info message and exit
    if not matched_items:
        messagebox.showinfo("Value Not Found", f"The value '{search_term}' could not be found.")
        return

    # Clear current items in the listbox
    selected_value_listbox.delete(0, tk.END)

    # Insert only the matched items without selecting any
    for item in matched_items:
        selected_value_listbox.insert(tk.END, item)

    # Scroll to the first match, but don't select
    if matched_items:
        selected_value_listbox.activate(0)
        selected_value_listbox.see(0)


search_button = tk.Button(filter_frame, text="Search", command=filter_listbox)
search_button.pack(pady=10)

# Scrollbar for the Listbox
listbox_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Attach the scrollbar to the Listbox
selected_value_listbox.config(yscrollcommand=listbox_scrollbar.set)
listbox_scrollbar.config(command=selected_value_listbox.yview)

# Button to filter data
filter_button = tk.Button(filter_frame, text="Filter Data", command=filter_data)
filter_button.pack(pady=20)

# Bind column selection to populate unique values
selected_column.trace('w', populate_unique_values)

# Submit button
submit_button = tk.Button(root, text="Submit data", font=('Times New Roman', 12), bg='orange')
submit_button.place(relx=0.5, rely=0.67, anchor='center')  # Center the button and position it 1/3 from the bottom

# Excel-like display below the submit button
table_display_frame = tk.Frame(root, bg='lightblue')  # Set the background color to light blue
table_display_frame.place(relx=0.5, rely=0.85 + 19 / 700, anchor='center')  # Added 0.5 cm gap (19px)

# Create a Treeview for the table
tree = ttk.Treeview(table_display_frame, show='headings', height=8)  # Increased height for visibility
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a custom style for the Treeview
style = ttk.Style(root)
style.configure("Treeview.Heading", font=('Times New Roman', 10, 'bold'))  # Set bold font for headings
style.theme_use('clam')

# Add a scrollbar
scrollbar = ttk.Scrollbar(table_display_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill='y')
tree.configure(yscrollcommand=scrollbar.set)

root.mainloop()