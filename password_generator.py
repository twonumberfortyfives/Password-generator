import random
import string
import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import simpledialog

# Создание базы данных и таблицы при необходимости
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username text, password text, note text )''')

c.execute('''CREATE TABLE IF NOT EXISTS password_history
             (username text, password text, note text)''')

conn.commit()
conn.close()

def save_user_to_db(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def open_main_window():
    global username
    login_register_window.withdraw()
    main_window.deiconify()
    error_label.config(text="")
    username = login_register_entry.get()

def login_or_register():
    global username
    username = login_register_entry.get()
    password = login_register_password_entry.get()

    if login_mode.get() == 1:  # Режим входа
        user = check_user(username, password)
        if user:
            open_main_window()
        else:
            error_label.config(text="Wrong login or password!")
    elif login_mode.get() == 2:  # Режим регистрации
        if username and password:
            save_user_to_db(username, password)
            open_main_window()

def generate_password(length=12):
    all_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(all_characters) for _ in range(length))
    return password

def copy_to_clipboard():
    generated_password = result_label.cget("text")[19:]
    main_window.clipboard_clear()
    main_window.clipboard_append(generated_password)
    main_window.update()

def generate_button_clicked(): 
    global username
    length = int(entry.get())
    generated_password = generate_password(length)
    note = simpledialog.askstring("Note", "Add a note for this password:")

    save_password_to_history(username, generated_password, note)
    
    result_label.config(text=f"Here your password: {generated_password}")

def save_password_to_history(username, password, note):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO password_history (username, password, note) VALUES (?, ?, ?)", (username, password, note))
    conn.commit()
    conn.close()
    
def get_password_history(username): 
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM password_history WHERE username=?", (username,))   
    history = c.fetchall()
    conn.close()
    return history

def view_password_history():
    global username, history, history_listbox
    history = get_password_history(username)

    history_window = tk.Toplevel(main_window)
    history_window.title("Password History")
    history_window.geometry("530x330")
    history_window.resizable(width=False,height=False)
    

    history_listbox = tk.Listbox(history_window, width=50, height=15)
    
    history_listbox.pack(pady=10)

    for entry in history:
        history_listbox.insert(tk.END, f"Password: {entry[1]}, Note: {entry[2]}")
        
    copy_button = ttk.Button(history_window, text="Copy Password", command=copy_selected_password)
    copy_button.pack(pady=10)

def view_generated_codes():
    global username
    codes = get_password_history(username)

    codes_window = tk.Toplevel(main_window)
    codes_window.title("Generated Codes History")
    codes_window.geometry("530x330")
    codes_window.resizable(height=False,width=False)

    codes_listbox = tk.Listbox(codes_window, width=50, height=15)
    codes_listbox.pack(pady=10)

    for entry in codes:
        codes_listbox.insert(tk.END, f"Password: {entry[1]}, Note: {entry[2]}")
        
def copy_selected_password():
    selected_item = history_listbox.curselection()
    if selected_item:
        selected_password = history[selected_item[0]][1]
        main_window.clipboard_clear()
        main_window.clipboard_append(selected_password)
        main_window.update()

login_register_window = tk.Tk()
login_register_window.title("Sign in or Log in")
login_register_window.geometry("530x330")
login_register_window.resizable(False, False)

style = ttk.Style()
style.configure('TButton', font=('Arial', 12))

login_register_label = ttk.Label(login_register_window, text="Username:")
login_register_entry = ttk.Entry(login_register_window)

login_register_password_label = ttk.Label(login_register_window, text="Password:")
login_register_password_entry = ttk.Entry(login_register_window, show="*")

login_mode = tk.IntVar()

login_radio = ttk.Radiobutton(login_register_window, text="Log in", variable=login_mode, value=1)
register_radio = ttk.Radiobutton(login_register_window, text="Sign in", variable=login_mode, value=2)

login_register_button = ttk.Button(login_register_window, text="Continue", command=login_or_register)

login_register_label.pack(pady=10)
login_register_entry.pack(pady=10)
login_register_password_label.pack(pady=10)
login_register_password_entry.pack(pady=10)
login_radio.pack(pady=5)
register_radio.pack(pady=5)
login_register_button.pack(pady=10)

error_label = ttk.Label(login_register_window, text="Welcome", foreground="red",borderwidth=0)
error_label.pack(pady=0)

main_window = tk.Tk()
main_window.title("Password Generator")
main_window.geometry("530x330")
main_window.withdraw()
main_window.resizable(width=False, height=False)

view_all_passwords_button = ttk.Button(main_window, text="View All Passwords", command=view_password_history)
view_all_passwords_button.pack(pady=10)

label = ttk.Label(main_window, text="Enter the length of password:")
entry = ttk.Entry(main_window)
generate_button = ttk.Button(main_window, text="Generate", command=generate_button_clicked)
result_label = ttk.Label(main_window, text="Your password: ")
copy_button = ttk.Button(main_window, text="Copy", command=copy_to_clipboard) 

label.pack(pady=10)
entry.pack(pady=10) 
generate_button.pack(pady=10)
result_label.pack(pady=10)
copy_button.pack(pady=10)

login_register_window.mainloop()
