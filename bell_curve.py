import random
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import statistics
import csv

simulation_count = 0
fig = None 

# --- Core Logic ---
def simulate_normal_draws_one_by_one(num_draws, mean=50, std_dev=15):
    """Yield one normal value at a time."""
    for _ in range(num_draws):
        yield random.gauss(mean, std_dev)

def plot_distribution_tk(data, title, ax):
    """Plot distribution on a given Matplotlib axes."""
    ax.hist(data, bins=30, edgecolor='white', color='#388e3c', density=True)
    ax.set_xlabel("Generated Numbers", fontsize=10, color='white')
    ax.set_ylabel("Density", fontsize=10, color='white')
    ax.set_title(title, fontsize=12, fontweight='bold', color='white')
    ax.grid(True, linestyle='--', alpha=0.7, color='#a5d6a7')
    ax.tick_params(axis='both', colors='white')
    ax.set_facecolor('#1b5e20')  


# --- GUI Logic ---
def export_to_csv(data, mean_val, std_dev_val, simulation_num):
    """Export simulation data to CSV."""
    filename = f"simulation_{simulation_num}.csv"
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Draw Number", "Value"])
        for i, val in enumerate(data, 1):
            writer.writerow([i, f"{val:.2f}"])
        writer.writerow([])
        writer.writerow(["Mean", f"{mean_val:.2f}"])
        writer.writerow(["Standard Deviation", f"{std_dev_val:.2f}"])
    messagebox.showinfo("CSV Saved", f"Simulation data saved to {filename}.")

def save_plot():
    """Save the plot to a file."""
    global fig  

    if fig is None:
        messagebox.showerror("Error", "No plot to save. Run a simulation first.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"),
                                                            ("JPEG files", "*.jpg"),
                                                            ("PDF files", "*.pdf"),
                                                            ("All files", "*.*")])
    if file_path:
        try:
            fig.savefig(file_path)  
            messagebox.showinfo("Plot Saved", f"Plot saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error Saving Plot", str(e))

def run_simulation():
    global simulation_count
    global fig 
    simulation_count += 1

    try:
        num_students = int(entry_students.get())
        draws_per_student = int(entry_draws.get())

        if num_students <= 0 or draws_per_student <= 0:
            raise ValueError("Both values must be positive integers.")
        if num_students > 1000:
            raise ValueError("Number of students should not exceed 1000.")
        if draws_per_student > 1000:
            raise ValueError("Number of draws per student should not exceed 1000.")

    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))
        return

    total_draws = num_students * draws_per_student
    text_output.delete(1.0, tk.END)
    run_button.config(state="disabled")
    reset_button.config(state="disabled")
    entry_students.config(state="disabled")  
    entry_draws.config(state="disabled")
    save_button.config(state="disabled") 

    root.after(0, show_loading_animation)  

    def simulate_and_display():
        global fig 

        data = []
        gen = simulate_normal_draws_one_by_one(total_draws)
        for i, value in enumerate(gen, 1):
            data.append(value)
            text_output.insert(tk.END, f"Draw {i}: {value:.2f}\n")
            text_output.see(tk.END)
            time.sleep(0.01)  

        mean_value = statistics.mean(data)
        std_dev_value = statistics.stdev(data)

        text_output.insert(tk.END, f"\nMean: {mean_value:.2f}\n", "output_stats")
        text_output.insert(tk.END, f"\nStandard Deviation: {std_dev_value:.2f}\n", "output_stats")

       
        fig, ax = plt.subplots(figsize=(8, 4), facecolor='#1b5e20')  
        plot_distribution_tk(data, f"{num_students} Students × {draws_per_student} Draws Each", ax)
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

        export_to_csv(data, mean_value, std_dev_value, simulation_count)

        root.after(0, lambda: run_button.config(state="normal"))
        root.after(0, lambda: reset_button.config(state="normal"))
        root.after(0, lambda: entry_students.config(state="normal"))  
        root.after(0, lambda: entry_draws.config(state="normal"))
        root.after(0, lambda: save_button.config(state="normal")) 

        root.after(0, hide_loading_animation)  

    threading.Thread(target=simulate_and_display).start()

def reset_simulation():
    entry_students.delete(0, tk.END)
    entry_draws.delete(0, tk.END)
    text_output.delete(1.0, tk.END)
    # Clear the plot frame
    for widget in plot_frame.winfo_children():
        widget.destroy()
    entry_students.config(state="normal")
    entry_draws.config(state="normal")
    save_button.config(state="disabled") 
    root.after(0, hide_loading_animation) 

def validate_input(event):
    """Validates input to allow only integers."""
    value = event.widget.get()
    if not value.isdigit() and value != "":
        event.widget.delete(len(value)-1, tk.END)

def show_loading_animation():
    progress_bar.pack(pady=10)  
    progress_bar.start()

def hide_loading_animation():
    progress_bar.stop()
    progress_bar.pack_forget()  

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("Bell Curve Simulation")
root.geometry("820x750")
root.configure(bg="#e8f5e9") 

# Style for ttk widgets (Progressbar)
style = ttk.Style()
style.theme_use('clam')  
style.configure("TProgressbar",
    background="white", 
    troughcolor="#388e3c",  
    bordercolor="white",
    lightcolor="white",
    darkcolor="white")


# Load Poppins font (ensure it's installed or bundled)
try:
    root.option_add("*font", ('Poppins', 12))
except tk.TclError:
    print("Poppins font not found. Using default font.")

# Title Label
title_label = tk.Label(
    root, text="Bell Curve Simulator", bg="#e8f5e9",
    font=('Times New Roman', 26, "bold"), fg="#2e7d32", pady=30
)
title_label.pack()

# Input Frame
input_frame = tk.LabelFrame(root, text="Simulation Parameters", font=('Times New Roman', 16), bg="#e8f5e9", fg="#2e7d32", padx=20, pady=20, borderwidth=2, relief=tk.GROOVE)
input_frame.pack(pady=15, padx=20, fill="x")

# Center the content within the input frame
input_frame.columnconfigure(0, weight=1)
input_frame.columnconfigure(1, weight=1)

# Number of Students
tk.Label(input_frame, text="Number of Students:", font=('Times New Roman', 14), bg="#e8f5e9", fg="#388e3c").grid(row=0, column=0, padx=10, pady=10, sticky='e')
entry_students = tk.Entry(input_frame, font=('Times New Roman', 14), width=15, bg="white", fg="#1b5e20", highlightthickness=1, highlightbackground="#c8e6c9", highlightcolor="#388e3c", borderwidth=0, relief=tk.FLAT)  # Rounded corners
entry_students.grid(row=0, column=1, padx=10, pady=10, sticky='w')
entry_students.bind("<KeyRelease>", validate_input)  

# Draws per Student
tk.Label(input_frame, text="Draws per Student:", font=('Times New Roman', 14), bg="#e8f5e9", fg="#388e3c").grid(row=1, column=0, padx=10, pady=10, sticky='e')
entry_draws = tk.Entry(input_frame, font=('Times New Roman', 14), width=15, bg="white", fg="#1b5e20", highlightthickness=1, highlightbackground="#c8e6c9", highlightcolor="#388e3c", borderwidth=0, relief=tk.FLAT) # Rounded corners
entry_draws.grid(row=1, column=1, padx=10, pady=10, sticky='w')
entry_draws.bind("<KeyRelease>", validate_input) 

# Button Frame
button_frame = tk.Frame(root, bg="#e8f5e9", pady=10)
button_frame.pack(anchor='e', padx=20)  

button_padx = 15  
button_pady = 7   
button_font = ('Times New Roman', 12, "bold") 
button_bd = 0
button_highlightthickness = 0
button_cursor = "hand2"

reset_button = tk.Button(
    button_frame,
    text="Reset",
    font=button_font,
    bg="#808080",
    fg="white",
    padx=button_padx,
    pady=button_pady,
    command=reset_simulation,
    relief=tk.RAISED,
    borderwidth=2,
    activebackground="#A9A9A9",  
    activeforeground="white",
    bd=button_bd,
    highlightthickness=button_highlightthickness,
    cursor=button_cursor
)
reset_button.pack(side=tk.RIGHT, padx=10)

run_button = tk.Button(
    button_frame,
    text="Run Simulation",
    font=button_font,
    bg="#388e3c",
    fg="white",
    padx=button_padx,
    pady=button_pady,
    command=run_simulation,
    relief=tk.RAISED,
    borderwidth=2,
    activebackground="#43a047",
    activeforeground="white",
    bd=button_bd,
    highlightthickness=button_highlightthickness,
    cursor=button_cursor
)
run_button.pack(side=tk.RIGHT, padx=10)

save_button = tk.Button(
    button_frame,
    text="Save Plot",
    font=button_font,
    bg="#388e3c", 
    fg="white", 
    padx=button_padx,
    pady=button_pady,
    command=save_plot,
    relief=tk.RAISED,
    borderwidth=2,
    activebackground="#43a047", 
    activeforeground="white",
    bd=button_bd,
    highlightthickness=button_highlightthickness,
    cursor=button_cursor, 
)

save_button.pack(side=tk.RIGHT, padx=10)

# Apply border radius workaround for rounded corners
def make_round(widget, radius=50):
    """Makes the button rounded.  Radius controls the roundness."""
    try:
        widget.config(relief="raised", borderwidth=4, highlightbackground=widget['bg'], highlightcolor=widget['bg'])
        widget.bind("<Enter>", lambda e: widget.config(relief="ridge"))
        widget.bind("<Leave>", lambda e: widget.config(relief="raised"))
    except tk.TclError:
        print("Warning: Rounded button corners might not be fully supported on this platform.")

make_round(reset_button)
make_round(run_button)
make_round(save_button)

# Output and Plot Frames
output_plot_frame = tk.Frame(root, bg="#e8f5e9")
output_plot_frame.pack(pady=15, padx=20, fill="both", expand=True)

# Scrollable Output
output_frame = tk.LabelFrame(output_plot_frame, text="Simulation Output", font=('Times New Roman', 16), bg="#e8f5e9", fg="#2e7d32", padx=10, pady=10, borderwidth=2, relief=tk.GROOVE)
output_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10))
text_output = scrolledtext.ScrolledText(output_frame, width=40, height=15, font=('Consolas', 10), bg="#e5f4e7", fg="#1b5e20", borderwidth=1, relief=tk.SUNKEN)
text_output.pack(fill="both", expand=True)
text_output.tag_config("output_stats", font=('Times New Roman', 12, "bold"), foreground="#2e7d32")

# Plot Display Area
plot_frame = tk.LabelFrame(output_plot_frame, text="Distribution Plot", font=('Times New Roman', 16), bg="#e8f5e9", fg="#2e7d32", padx=10, pady=10, borderwidth=2, relief=tk.GROOVE)
plot_frame.pack(side=tk.RIGHT, fill="both", expand=True)

# Progress Bar
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='indeterminate')  

# Start GUI loop
root.mainloop()