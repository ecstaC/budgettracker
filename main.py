import tkinter as tk
from tkinter import messagebox
import mysql.connector
import matplotlib.pyplot as plt
from tkinter import ttk

# Global variables
entries = []  

# MySQL database connection
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='budgettracker',     
        password='BudgetTracker',  
        database='budget_tracker'
    )
    print("Connected to MySQL!")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    conn = None

if conn:
    cursor = conn.cursor()

    # Creating a table for entries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE,
            income DOUBLE,
            expense DOUBLE,
            category VARCHAR(255)
        )
    ''')
    conn.commit()
    
# Entry Widgets
income_entry = None
expense_entry = None
date_entry = None  

def main():
    global income_entry, expense_entry, date_entry, root # Declare as global variables

    root = tk.Tk()
    root.title("Personal Budget Tracker")

    # Income Section
    income_label = tk.Label(root, text="Income:")
    income_label.grid(row=0, column=0, padx=10, pady=10)
    income_entry = tk.Entry(root)
    income_entry.grid(row=0, column=1, padx=10, pady=10)

    # Expense Section
    expense_label = tk.Label(root, text="Expense:")
    expense_label.grid(row=1, column=0, padx=10, pady=10)
    expense_entry = tk.Entry(root)
    expense_entry.grid(row=1, column=1, padx=10, pady=10)

    # Category Section
    category_label = tk.Label(root, text="Category:")
    category_label.grid(row=2, column=0, padx=10, pady=10)
    category_entry = ttk.Combobox(root, values=["Groceries", "Utilities", "Entertainment", "Other"])
    category_entry.grid(row=2, column=1, padx=10, pady=10)

    # Date Entry
    date_label = tk.Label(root, text="Date (YYYY-MM-DD):")
    date_label.grid(row=0, column=2, padx=10, pady=10)
    date_entry = tk.Entry(root)
    date_entry.grid(row=0, column=3, padx=10, pady=10)

    # Add Expense Button
    add_expense_button = tk.Button(root, text="Add Expense", command=lambda: add_expense(category_entry.get()))
    add_expense_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Show Summary Button
    show_summary_button = tk.Button(root, text="Show Summary", command=show_summary)
    show_summary_button.grid(row=4, column=0, columnspan=2, pady=10)

    root.mainloop()

def add_expense(category):
    global income_entry, expense_entry, date_entry  # Declare as global variables

    date = date_entry.get()
    income = income_entry.get()
    expense = expense_entry.get()

    if date and (income or expense):
        # Insert the entry into the MySQL database with date, income, and category
        cursor.execute('INSERT INTO entries (date, income, expense, category) VALUES (%s, %s, %s, %s)', (date, float(income), float(expense), category))
        conn.commit()

        entries.append({"Date": date, "Income": float(income), "Expense": float(expense), "Category": category})
        messagebox.showinfo("Success", "Expense added successfully!")
    else:
        messagebox.showwarning("Warning", "Please enter both date and either income or expense.")

    # Clear entry fields
    date_entry.delete(0, tk.END)
    income_entry.delete(0, tk.END)
    expense_entry.delete(0, tk.END)

def show_summary():
    if not entries:
        messagebox.showinfo("Summary", "No data available.")
        return

    # Fetch data from the MySQL database
    cursor.execute('SELECT category, SUM(income), SUM(expense) FROM entries GROUP BY category')
    fetched_entries = cursor.fetchall()

    summary_text = ""
    for entry in fetched_entries:
        category, total_income, total_expense = entry
        summary_text += f"Category: {category}\nTotal Income: {total_income}\nTotal Expense: {total_expense}\n\n"

    messagebox.showinfo("Summary", summary_text)

    # Plot pie chart
    plot_data(fetched_entries)

def plot_data(fetched_entries):
    labels = [entry[0] for entry in fetched_entries]
    sizes_income = [entry[1] for entry in fetched_entries]
    sizes_expense = [entry[2] for entry in fetched_entries]
    colors = ['#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']

    # Plot pie chart for income
    plt.subplot(1, 2, 1)
    plt.pie(sizes_income, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.axis('equal')
    plt.title('Income by Category')

    # Plot pie chart for expense
    plt.subplot(1, 2, 2)
    plt.pie(sizes_expense, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.axis('equal')
    plt.title('Expense by Category')

    plt.show()

if __name__ == "__main__":
    main()
