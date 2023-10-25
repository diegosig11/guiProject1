import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askstring  # Import the askstring function for user input
from PIL import ImageTk, Image
from tkinter import messagebox
import re



def display_tutorial():
    tutorial_window = tk.Toplevel(root)
    tutorial_window.title("Tutorial")
    
    tutorial_text = """
    Step 1: Add Resistors
    - Click the 'Add Series Resistor' or 'Add Parallel Resistor' button to add resistors.
    - You can specify material properties for each resistor.

    Step 2: Set Material Properties
    - Select 'Conduction' or 'Convection' for each material.
    - Enter thermal conductivity, area, length, and convection coefficient.

    Step 3: Enter Temperatures
    - Set the environmental temperatures 

    Step 4: Solve
    - Click the 'Solve' button to calculate thermal resistance and heat flux.

    Step 5: Select Resistors
    -Click the 'Select Resistor' button on the tab interface to highlight the specified resistor. 
    
    Step 6: Delete Resistors
    - Click the 'Select Resistor' button then 'Delete Resistor' button to remove the selected resistor.

    Step 7: Tutorial Completed
    - Follow these steps to use the GUI effectively.
    """

    tutorial_label = tk.Label(tutorial_window, text=tutorial_text, padx=10, pady=10)
    tutorial_label.pack()

def get_mouse_location(event):
    screen_x, screen_y = root.winfo_pointerxy()  # Get mouse location relative to screen
    window_x = screen_x - root.winfo_x()  # Adjust to be relative to the window
    window_y = screen_y - root.winfo_y()

    # Ensure the coordinates are within the window's dimensions
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    window_x = max(0, min(window_x, window_width))
    window_y = max(0, min(window_y, window_height))

    print(f"Mouse Location (Relative to Window): X={window_x}, Y={window_y}")

class CustomNotebook(ttk.Notebook):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tab_event_callbacks = {}

    def bind_tab_event(self, tab_name, event, callback):
        self.tab_event_callbacks[tab_name] = callback
        self.bind(f"<<NotebookTabChanged-{tab_name}>>", lambda e: self.tab_event_callbacks[tab_name](e))

class ThermalResistor:
    def __init__(self, canvas, x, y, tab_name, resistor_type,size=(70, 50)):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = size[0]  # Width of the resistor
        self.height = size[1]  # Height of the resistor
        self.resistor_type = resistor_type  # Added resistor type attribute

        # Load and display the image
        self.image = Image.open("Resistor.jpg")
        self.image = self.image.resize(size)
        self.photo = ImageTk.PhotoImage(self.image)

        # Create an image widget on the canvas
        self.image_widget = canvas.create_image(x, y, anchor="nw", image=self.photo)

        # Create a rectangle to serve as a border
        self.border_rect = canvas.create_rectangle(x, y, x + self.width, y + self.height, outline="black", width=2)

        # New attribute to track selection state
        self.selected = False
        self.selection_rectangle = None
        self.tab_name = tab_name

        self.resistivity_var = tk.StringVar()
        self.resistivity_var.set("Conduction")

        

    def toggle_selected(self):
        self.selected = not self.selected
        outline_color = "red" if self.selected else "black"
        self.canvas.itemconfig(self.border_rect, outline=outline_color)



class ThermalResistorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Thermal Resistance")
        self.root.geometry("1400x800")

        self.canvas = tk.Canvas(root, width=500, height=300)
        self.canvas.pack()


        self.resistors = []
        self.material_names = []

        # Track the currently selected resistor
        self.selected_resistor = None


        tutorial_button = tk.Button(root, text="Tutorial", command=display_tutorial)
        tutorial_button.pack()

        self.add_resistor_button = tk.Button(root, text="Add Series Resistor", command=self.add_resistor)
        self.add_resistor_button.pack()

        self.add_parallel_resistor_button = tk.Button(root, text="Add Parallel Resistor", command=self.add_parallel_resistor)
        self.add_parallel_resistor_button.pack()

        self.solve_button = tk.Button(root, text="Solve", command=self.solve)
        self.solve_button.pack()

        self.delete_button = tk.Button(root, text="Delete Resistor", command=self.delete_resistor)
        self.delete_button.pack()

        # Create a separate frame for the Treeview widget on the right side
        self.result_frame = tk.Frame(root)
        self.result_frame.pack(side="right", padx=10)

        self.material_tree = ttk.Treeview(self.result_frame, columns=("Name", "Type", "Resistance", "Heat Flux", "Total Resistance", "Total Heat Flux"), show="headings")
        self.material_tree.heading("Name", text="Name")
        self.material_tree.heading("Type", text="Type")
        self.material_tree.heading("Resistance", text="Resistance")
        self.material_tree.heading("Heat Flux", text="Heat Flux")
        self.material_tree.heading("Total Resistance", text="Total Resistance")
        self.material_tree.heading("Total Heat Flux", text="Total Heat Flux")

        # Set the column widths
        self.material_tree.column("Name", width=100)  # Adjust the width as needed
        self.material_tree.column("Type", width=100)  # Adjust the width as needed
        self.material_tree.column("Resistance", width=150)  # Adjust the width as needed
        self.material_tree.column("Heat Flux", width=150)  # Adjust the width as needed
        self.material_tree.column("Total Resistance", width=100)  # Adjust the width as needed
        self.material_tree.column("Total Heat Flux", width=100)  # Adjust the width as needed
        

        self.material_tree.pack()

        self.modify_frame = ttk.Notebook(root)
        self.modify_frame.pack()

        self.material_entries = []  # Initialize material property entries list

        self.create_home_page()

        # Bind the tab changing event to the callback function
        self.modify_frame.bind("<<NotebookTabChanged>>", self.on_tab_change)  # Bind tab change event
        self.selected_resistor = None  # Store the selected resistor



    def on_tab_change(self, event):
        # Handle tab change here
        current_tab_index = self.modify_frame.index(self.modify_frame.select())
        if current_tab_index < len(self.resistors):
            if self.selected_resistor:
                self.selected_resistor.toggle_selected()
            self.selected_resistor = self.resistors[current_tab_index]
            self.selected_resistor.toggle_selected()

    def create_home_page(self):
        home_page = tk.Frame(self.modify_frame)
        self.modify_frame.add(home_page, text="Home Page")

        tk.Label(home_page, text="Environment Temperatures").pack()

        self.environment_temperatures = [tk.Entry(home_page), tk.Entry(home_page)]
        for i, entry in enumerate(self.environment_temperatures):
            tk.Label(home_page, text=f"Temperature {i + 1}:").pack()
            entry.pack()


        num_materials = len(self.resistors)
        num_input_fields = num_materials * 2
        self.temperature_entries = []

        for i in range(num_input_fields):
            tk.Label(home_page, text=f"Material Surface Temperature {i + 1}:").pack()
            temp_entry = tk.Entry(home_page)
            temp_entry.pack()
            self.temperature_entries.append(temp_entry)

    def add_resistor(self):
        x = 30 + len(self.resistors) * 70
        y = 150

        resistor_type = "Series"

        tab_name = askstring("Tab Name", "Enter a name for the tab:")
        if tab_name is not None:
            tab_name = str(tab_name) + " (Series)"

        tab = tk.Frame(self.modify_frame)
        self.modify_frame.add(tab, text=f"{tab_name} ")

        # Create a unique tab identifier
        tab_id = len(self.resistors)

        resistor = ThermalResistor(self.canvas, x, y, tab_id, "series",size=(65, 50))  # Set the resistor type to "series"
        self.resistors.append(resistor)

        select_button = tk.Button(tab, text="Select Resistor", command=lambda resistor=resistor: self.select_resistor(resistor))
        select_button.grid(row=0, column=0)

        # Bind a click event to the tab to highlight the resistor
        tab.bind("<Button-1>", lambda event, resistor=resistor: self.highlight_resistor(event, resistor))

        material_frame = tk.Frame(tab)
        material_frame.grid(padx=10, pady=10)

        resistivity_var = tk.StringVar()
        resistivity_var.set("Conduction")
            
        def update_resistivity_type():
            resistivity_type = resistivity_var.get()  # Get the selected resistivity type
            print(f"Resistivity Type: {resistivity_type}")

        conduction_radio = tk.Radiobutton(material_frame, text="Conduction", variable=resistivity_var, value="Conduction", command=update_resistivity_type)
        convection_radio = tk.Radiobutton(material_frame, text="Convection", variable=resistivity_var, value="Convection", command=update_resistivity_type)

        conduction_radio.grid(row=0, column=0)
        convection_radio.grid(row=0, column=1)

        tk.Label(material_frame, text="Thermal Conductivity:").grid(row=1, column=0, padx=5, pady=5)
        conductivity_entry = tk.Entry(material_frame)
        conductivity_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(material_frame, text="Area:").grid(row=2, column=0, padx=5, pady=5)
        area_entry = tk.Entry(material_frame)
        area_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(material_frame, text="Length:").grid(row=3, column=0, padx=5, pady=5)
        length_entry = tk.Entry(material_frame)
        length_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(material_frame, text="Convection Coefficient:").grid(row=4, column=0, padx=5, pady=5)
        convection_coeff_entry = tk.Entry(material_frame)
        convection_coeff_entry.grid(row=4, column=1, padx=5, pady=5)



        self.material_entries.append((resistivity_var, conductivity_entry, area_entry, length_entry, convection_coeff_entry))
        self.material_names.append(tab_name)  # Add material name


    def select_resistor(self, resistor):
        # Select the specified resistor
        if self.selected_resistor:
            self.selected_resistor.toggle_selected()
        self.selected_resistor = resistor
        self.selected_resistor.toggle_selected()

    def update_selected_resistor(self, event):
        # Retrieve the currently selected tab
        current_tab_index = self.modify_frame.index(self.modify_frame.select())
        if current_tab_index < len(self.resistors):
            # Update the selected resistor
            if self.selected_resistor:
                self.selected_resistor.toggle_selected()
            self.selected_resistor = self.resistors[current_tab_index]
            self.selected_resistor.toggle_selected()

    def highlight_resistor(self, event, resistor):
        if self.selected_resistor:
            self.selected_resistor.toggle_selected()  # Un-highlight the previously selected resistor

        self.selected_resistor = resistor
        self.selected_resistor.toggle_selected()  # Highlight the newly selected resistor
        print(f"highlight_resistor called for {resistor.tab_name}")

        # Check if the tab name contains "Parallel" and highlight the border if it does
        if "Parallel" in resistor.tab_name:
            self.selected_resistor.toggle_selected()

    # In the add_parallel_resistor function:
    def add_parallel_resistor(self):
        # Use askstring to get the names for the two material tabs
        tab_name_1 = askstring("Tab Name", "Enter a name for the top resistor:")
        if tab_name_1 is not None:
            tab_name_1 = str(tab_name_1) + " (Parallel)"

        tab_name_2 = askstring("Tab Name", "Enter a name for the bottom resistor:")
        if tab_name_2 is not None:
            tab_name_2 = str(tab_name_2) + " (Parallel)"

        if tab_name_1 is None or tab_name_2 is None:  # User canceled
            return
        
        
        # Create a tab for the first resistor
        tab1 = tk.Frame(self.modify_frame)
        self.modify_frame.add(tab1, text=f"{tab_name_1}")

        # Load and display the "Resistor.jpg" image on the canvas for the first resistor
        x1 = 80 + len(self.resistors) * 70  # Set the initial x-coordinate
        y1 = 100  # Position parallel resistors vertically


        image1 = Image.open("Resistor.jpg")
        photo1 = ImageTk.PhotoImage(image1)
        image_widget1 = self.canvas.create_image(x1, y1, anchor="nw", image=photo1)

        resistivity_var1 = tk.StringVar()
        resistivity_var1.set("Conduction")

        conduction_radio1 = tk.Radiobutton(tab1, text="Conduction", variable=resistivity_var1, value="Conduction")
        convection_radio1 = tk.Radiobutton(tab1, text="Convection", variable=resistivity_var1, value="Convection")

        conduction_radio1.grid(row=0, column=0)
        convection_radio1.grid(row=0, column=1)

        tk.Label(tab1, text="Thermal Conductivity:").grid(row=1, column=0, padx=5, pady=5)
        conductivity_entry1 = tk.Entry(tab1)
        conductivity_entry1.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(tab1, text="Area:").grid(row=2, column=0, padx=5, pady=5)
        area_entry1 = tk.Entry(tab1)
        area_entry1.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(tab1, text="Length:").grid(row=3, column=0, padx=5, pady=5)
        length_entry1 = tk.Entry(tab1)
        length_entry1.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(tab1, text="Convection Coefficient:").grid(row=4, column=0, padx=5, pady=5)
        convection_coeff_entry1 = tk.Entry(tab1)
        convection_coeff_entry1.grid(row=4, column=1, padx=5, pady=5)

        self.material_entries.append((resistivity_var1, conductivity_entry1, area_entry1, length_entry1, convection_coeff_entry1))
        self.material_names.append(tab_name_1)  # Add material name

        # Store the image widget in the resistor's placeholder
        resistor1 = ThermalResistor(self.canvas, x1, y1, len(self.resistors), "parallel",size=(65, 60))  # Set the resistor type to "parallel"
        self.resistors.append(resistor1)
        self.resistors[-1].image_widget = image_widget1  # Set the image widget
        self.resistors[-1].photo = photo1  # Set the photo
        self.resistors[-1].image = image1  # Set the image

        select_button1 = tk.Button(tab1, text="Select Resistor", command=lambda resistor=resistor1: self.select_resistor(resistor))
        select_button1.grid(row=0, column=2)

        # Create a tab for the second resistor
        tab2 = tk.Frame(self.modify_frame)
        self.modify_frame.add(tab2, text=f"{tab_name_2}")

        # Load and display the "Resistor.jpg" image on the canvas for the second resistor
        x2 = 10 + len(self.resistors) * 70  # Set a different initial x-coordinate for the second parallel resistor
        y2 = 200  # Position parallel resistors vertically higher the number the lower it goes

        image2 = Image.open("Resistor.jpg")
        photo2 = ImageTk.PhotoImage(image2)
        image_widget2 = self.canvas.create_image(x2, y2, anchor="nw", image=photo2)

        resistivity_var2 = tk.StringVar()
        resistivity_var2.set("Conduction")

        conduction_radio2 = tk.Radiobutton(tab2, text="Conduction", variable=resistivity_var2, value="Conduction")
        convection_radio2 = tk.Radiobutton(tab2, text="Convection", variable=resistivity_var2, value="Convection")

        conduction_radio2.grid(row=0, column=0)
        convection_radio2.grid(row=0, column=1)

        tk.Label(tab2, text="Thermal Conductivity:").grid(row=1, column=0, padx=5, pady=5)
        conductivity_entry2 = tk.Entry(tab2)
        conductivity_entry2.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(tab2, text="Area:").grid(row=2, column=0, padx=5, pady=5)
        area_entry2 = tk.Entry(tab2)
        area_entry2.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(tab2, text="Length:").grid(row=3, column=0, padx=5, pady=5)
        length_entry2 = tk.Entry(tab2)
        length_entry2.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(tab2, text="Convection Coefficient:").grid(row=4, column=0, padx=5, pady=5)
        convection_coeff_entry2 = tk.Entry(tab2)
        convection_coeff_entry2.grid(row=4, column=1, padx=5, pady=5)


        self.material_entries.append((resistivity_var2, conductivity_entry2, area_entry2, length_entry2, convection_coeff_entry2))
        self.material_names.append(tab_name_2)  # Add material name

        # Store the image widget in the resistor's placeholder
        resistor2 = ThermalResistor(self.canvas, x2, y2, len(self.resistors), "parallel",size=(65, 50))  # Set the resistor type to "parallel"
        self.resistors.append(resistor2)
        self.resistors[-1].image_widget = image_widget2  # Set the image widget
        self.resistors[-1].photo = photo2  # Set the photo
        self.resistors[-1].image = image2  # Set the image

        select_button2 = tk.Button(tab2, text="Select Resistor", command=lambda resistor=resistor2: self.select_resistor(resistor))
        select_button2.grid(row=0, column=2)
        


    def delete_resistor(self):
        if self.selected_resistor:
            if self.selected_resistor in self.resistors:
                current_tab_index = self.modify_frame.index(self.modify_frame.select())
                tab_name = self.material_names[current_tab_index]
                # Check if the selected resistor's name contains "(Parallel)" or "(Series)"
                is_parallel_selected = "(Parallel)" in tab_name
                is_series_selected = "(Series)" in tab_name
                if is_parallel_selected:  # If the tab name contains "(Parallel)"
                    # Check if there is a resistor in front of it
                    if current_tab_index > 0:
                        # Forget the tabs associated with both resistors
                        self.modify_frame.forget(current_tab_index)
                        self.modify_frame.forget(current_tab_index)

                        self.selected_resistor.canvas.delete(self.selected_resistor.image_widget)
                        self.resistors[current_tab_index - 1].canvas.delete(self.resistors[current_tab_index].image_widget)

                        # Remove the selected resistor and the one in front of it from the list
                        self.resistors.pop(current_tab_index)
                        self.resistors.pop(current_tab_index)
                elif is_series_selected:
                     # If the tab name contains "(Series)" for a series resistor, just remove the selected resistor and its tab
                    self.selected_resistor.canvas.delete(self.selected_resistor.image_widget)
                    self.resistors.pop(current_tab_index)
                    self.modify_frame.forget(current_tab_index)

            # Unselect the selected resistor
            self.selected_resistor = None


    def solve(self):
        env_temperatures = [float(entry.get()) for entry in self.environment_temperatures]  # Convert to float

        # Function to safely convert an input to a float or return 0.0 for empty inputs
        def safe_float(input_str):
            if input_str.strip():  # Check if the input is not empty
                return float(input_str)
            else:
                return 0.0

        # Clear the previous entries in the Treeview widget
        for item in self.material_tree.get_children():
            self.material_tree.delete(item)

        series_resistance = []
        parallel_resistance = []

        for (resistivity_var, conductivity_entry, area_entry, length_entry, convection_coeff_entry), material_name in zip(self.material_entries, self.material_names):
            resistivity_type = resistivity_var.get()
            area = safe_float(area_entry.get())
            length = safe_float(length_entry.get())
            conduction_coeff = safe_float(conductivity_entry.get())
            convection_coeff = safe_float(convection_coeff_entry.get())

            if "Conduction" in resistivity_type:
                resistance = length / (area * conduction_coeff)
            elif "Convection" in resistivity_type:
                resistance = 1 / (area * convection_coeff)
            else:
                resistance = 0.0

            # Check if the resistors are in series or parallel based on the tab name
            if "Series" in material_name:
                series_resistance.append(resistance)
            elif "Parallel" in material_name:
                resistance = 1/resistance
                parallel_resistance.append(resistance)

            # Display the resistivity value in the Treeview
            self.material_tree.insert("", "end", values=(material_name, resistivity_type, resistance))

        total_series_resistance = sum(series_resistance)
        total_parallel_resistance = sum(parallel_resistance)
        total_parallel_resistance = 1/total_parallel_resistance

        # Calculate total heat flux using the total resistance
        if total_series_resistance > 0.0:
            total_resistance = total_series_resistance + total_parallel_resistance
            total_heat_flux = (env_temperatures[0] - env_temperatures[1]) / total_resistance
        else:
            # Handle the case when there are no series resistors
            total_resistance = float('inf')  # Set total_resistance to infinity
            total_heat_flux = 0.0  # No heat flux (division by infinity)

        # Display the total resistance and total heat flux as separate entries
        self.material_tree.insert("", "end", values=("Total Resistance", "N/A", total_resistance, total_heat_flux, "N/A", "N/A"))
        self.material_tree.insert("", "end", values=("Total Heat Flux", "N/A", "N/A", "N/A", total_resistance, total_heat_flux))

        # Show the results in a pop-up window
        result_message = f"Total Resistance: {total_resistance}\nTotal Heat Flux: {total_heat_flux}"
        messagebox.showinfo("Results", result_message)



if __name__ == "__main__":
    root = tk.Tk()
    app = ThermalResistorApp(root)
    root.mainloop()