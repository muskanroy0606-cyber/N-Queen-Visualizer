import tkinter as tk
from tkinter import ttk
import sqlite3
import os  

# Get path to database relative to this script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

def display_users():
    root = tk.Tk()
    root.title("Database Viewer - Users Table")
    root.geometry("600x400")
    root.configure(bg="#1e1e2e")
    
    # Configure styling for the Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", 
                    background="#282a36",
                    foreground="#f8f8f2",
                    rowheight=25,
                    fieldbackground="#282a36")
    style.map('Treeview', background=[('selected', '#bd93f9')])

    # Create Title
    tk.Label(root, text="Registered Users", font=("Segoe UI", 16, "bold"), fg="#bd93f9", bg="#1e1e2e").pack(pady=10)

    # Create Treeview frame
    tree_frame = tk.Frame(root)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # Scrollbar
    tree_scroll = tk.Scrollbar(tree_frame)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # Create Treeview
    tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended")
    tree.pack(fill=tk.BOTH, expand=True)
    tree_scroll.config(command=tree.yview)

    # Define Columns
    tree['columns'] = ("ID", "Gmail", "Password Hash")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("ID", anchor=tk.CENTER, width=50)
    tree.column("Gmail", anchor=tk.W, width=200)
    tree.column("Password Hash", anchor=tk.W, width=300)

    # Create Headings
    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("ID", text="ID", anchor=tk.CENTER)
    tree.heading("Gmail", text="Gmail", anchor=tk.W)
    tree.heading("Password Hash", text="Password Hash", anchor=tk.W)

    # Fetch Data from Database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        records = cursor.fetchall()
        
        for record in records:
            # We cut off the password hash so it fits nicely
            truncated_hash = record[2][:30] + "..." if len(record[2]) > 30 else record[2]
            tree.insert(parent='', index='end', iid=record[0], text='', values=(record[0], record[1], truncated_hash))
            
        conn.close()
    except Exception as e:
        tk.Label(root, text=f"Error connecting to database: {e}", fg="red", bg="#1e1e2e").pack()

    root.mainloop()

if __name__ == "__main__":
    display_users()
