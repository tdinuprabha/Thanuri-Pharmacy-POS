import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ---------------- DATABASE ---------------- #
conn = sqlite3.connect("thanuri_pharmacy.db")
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# Products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    quantity INTEGER,
    category TEXT,
    discount REAL,
    expiry_date TEXT
)
""")

# Sales table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    quantity INTEGER,
    total_price REAL,
    date TEXT
)
""")

# Default admin user
cursor.execute("SELECT * FROM users WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO users(username,password) VALUES('admin','1234')")
conn.commit()

# ---------------- LOGIN WINDOW ---------------- #
def login():
    username = user_entry.get()
    password = pass_entry.get()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    if cursor.fetchone():
        login_window.destroy()
        main_window()
    else:
        messagebox.showerror("Login Failed", "Invalid Credentials")

login_window = tk.Tk()
login_window.title("Thanuri Pharmacy")
login_window.geometry("400x350")
login_window.configure(bg="#6C63FF")

tk.Label(login_window,
         text="Thanuri Pharmacy 💊",
         font=("Segoe UI", 22, "bold"),
         bg="#6C63FF",
         fg="white").pack(pady=30)

tk.Label(login_window,
         text="Login to Continue",
         font=("Segoe UI", 12),
         bg="#6C63FF",
         fg="white").pack()

user_entry = ttk.Entry(login_window, width=25)
user_entry.pack(pady=15)
user_entry.insert(0,"admin")

pass_entry = ttk.Entry(login_window, width=25, show="*")
pass_entry.pack(pady=10)
pass_entry.insert(0,"1234")

ttk.Button(login_window, text="Login", command=login).pack(pady=20)

# ---------------- MAIN WINDOW ---------------- #
def main_window():
    root = tk.Tk()
    root.title("Thanuri Pharmacy Management System")
    root.geometry("1200x700")
    root.configure(bg="#F8F9FF")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

    # ---------- HEADER ---------- #
    header = tk.Frame(root, bg="#6C63FF", height=60)
    header.pack(fill="x")
    tk.Label(header,
             text="Thanuri Pharmacy POS System",
             font=("Segoe UI", 18, "bold"),
             bg="#6C63FF",
             fg="white").pack(pady=10)

    # ---------- DASHBOARD ---------- #
    dashboard = tk.Frame(root, bg="#F8F9FF")
    dashboard.pack(fill="x", pady=10)

    sales_label = tk.Label(dashboard,
                           font=("Segoe UI", 12, "bold"),
                           bg="#F8F9FF",
                           fg="#333")
    sales_label.pack(side="left", padx=20)

    product_label = tk.Label(dashboard,
                             font=("Segoe UI", 12, "bold"),
                             bg="#F8F9FF",
                             fg="#333")
    product_label.pack(side="left", padx=20)

    def load_dashboard():
        cursor.execute("SELECT SUM(total_price) FROM sales")
        total_sales = cursor.fetchone()[0]
        total_sales = total_sales if total_sales else 0

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        sales_label.config(text=f"💰 Total Sales: Rs {round(total_sales,2)}")
        product_label.config(text=f"📦 Total Products: {total_products}")

    # ---------- INVENTORY ---------- #
    inventory_frame = tk.LabelFrame(root,
                                    text="Inventory Management",
                                    bg="#F8F9FF",
                                    font=("Segoe UI", 12, "bold"))
    inventory_frame.pack(fill="x", padx=20, pady=10)

    entries = []

    labels = ["Name", "Price", "Quantity", "Category", "Discount (%)", "Expiry Date"]
    for i, text in enumerate(labels):
        tk.Label(inventory_frame, text=text, bg="#F8F9FF").grid(row=0, column=i)
        entry = ttk.Entry(inventory_frame, width=15)
        entry.grid(row=1, column=i, padx=5, pady=5)
        entries.append(entry)

    # ---------- FUNCTIONS ---------- #
    def load_products():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM products")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

    def add_product():
        cursor.execute("""
        INSERT INTO products(name,price,quantity,category,discount,expiry_date)
        VALUES(?,?,?,?,?,?)
        """, (entries[0].get(), entries[1].get(), entries[2].get(),
              entries[3].get(), entries[4].get(), entries[5].get()))
        conn.commit()
        load_products()
        load_dashboard()
        messagebox.showinfo("Success", "Product Added")

    def delete_product():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to delete")
            return

        values = tree.item(selected)["values"]
        product_id = values[0]

        confirm = messagebox.askyesno("Confirm Delete",
                                      "Are you sure you want to delete this product?")
        if confirm:
            cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            conn.commit()
            load_products()
            load_dashboard()
            messagebox.showinfo("Deleted", "Product deleted successfully")

    # ---------- BUTTONS ---------- #
    ttk.Button(inventory_frame, text="Add Product", command=add_product).grid(row=1, column=6, padx=5)
    ttk.Button(inventory_frame, text="Delete Product ❌", command=delete_product).grid(row=1, column=7, padx=5)

    # ---------- TABLE ---------- #
    columns = ("ID","Name","Price","Qty","Category","Discount","Expiry")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(fill="both", expand=True, padx=20)

    load_products()
    load_dashboard()

    # ---------- BILLING ---------- #
    billing_frame = tk.LabelFrame(root,
                                  text="Billing System",
                                  bg="#F8F9FF",
                                  font=("Segoe UI", 12, "bold"))
    billing_frame.pack(fill="x", padx=20, pady=10)

    tk.Label(billing_frame, text="Enter Quantity:", bg="#F8F9FF").pack(side="left", padx=10)
    bill_qty = ttk.Entry(billing_frame, width=10)
    bill_qty.pack(side="left")

    total_label = tk.Label(billing_frame,
                           text="Total: Rs 0",
                           font=("Segoe UI", 12, "bold"),
                           bg="#F8F9FF",
                           fg="#6C63FF")
    total_label.pack(side="left", padx=20)

    def generate_bill():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product")
            return

        values = tree.item(selected)["values"]
        price = float(values[2])
        discount = float(values[5])
        quantity = int(bill_qty.get())

        total = price * quantity
        total -= total * (discount / 100)

        total_label.config(text=f"Total: Rs {round(total,2)}")

        cursor.execute("""
        INSERT INTO sales(product_name,quantity,total_price,date)
        VALUES(?,?,?,?)
        """,(values[1], quantity, total, datetime.now()))
        conn.commit()
        load_dashboard()

    ttk.Button(billing_frame, text="Generate Bill 💵", command=generate_bill).pack(side="left", padx=10)

    root.mainloop()

login_window.mainloop()