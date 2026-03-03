import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def upload_db():
    db_name = entry_db.get().strip()
    user = entry_user.get().strip()
    password = entry_password.get().strip()
    host = entry_host.get().strip()
    port = entry_port.get().strip()
    file_path = entry_file.get().strip()

    if not all([db_name, user, password, host, port, file_path]):
        messagebox.showerror("Error", "All fields are required!")
        return

    # Set environment variable for password (avoids prompt)
    os.environ["PGPASSWORD"] = password

    try:
        # Restore database using psql
        cmd = [
            "psql",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", db_name,
            "-f", file_path
        ]
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", f"Database restored into '{db_name}' successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to restore database.\n{e}")
    finally:
        os.environ.pop("PGPASSWORD", None)


def browse_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("SQL files", "*.sql"), ("Dump files", "*.dump"), ("All files", "*.*")]
    )
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)


# Tkinter GUI
root = tk.Tk()
root.title("PostgreSQL Database Uploader")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="Database Name:").grid(row=0, column=0, sticky="w")
entry_db = tk.Entry(frame, width=40)
entry_db.grid(row=0, column=1)

tk.Label(frame, text="User:").grid(row=1, column=0, sticky="w")
entry_user = tk.Entry(frame, width=40)
entry_user.grid(row=1, column=1)

tk.Label(frame, text="Password:").grid(row=2, column=0, sticky="w")
entry_password = tk.Entry(frame, show="*", width=40)
entry_password.grid(row=2, column=1)

tk.Label(frame, text="Host:").grid(row=3, column=0, sticky="w")
entry_host = tk.Entry(frame, width=40)
entry_host.insert(0, "localhost")
entry_host.grid(row=3, column=1)

tk.Label(frame, text="Port:").grid(row=4, column=0, sticky="w")
entry_port = tk.Entry(frame, width=40)
entry_port.insert(0, "5432")
entry_port.grid(row=4, column=1)

tk.Label(frame, text="SQL/Dump File:").grid(row=5, column=0, sticky="w")
entry_file = tk.Entry(frame, width=40)
entry_file.grid(row=5, column=1)
btn_browse = tk.Button(frame, text="Browse", command=browse_file)
btn_browse.grid(row=5, column=2)

btn_upload = tk.Button(frame, text="Upload Database", command=upload_db, bg="green", fg="white")
btn_upload.grid(row=6, column=0, columnspan=3, pady=10)

root.mainloop()
