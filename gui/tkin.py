import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title('Styled Tkinter Test')

style = ttk.Style()
style.configure('TButton', foreground='green', background='white', font=('Arial', 12), padding=10)
style.configure('TLabel', foreground='black', font=('Helvetica', 14))

label = ttk.Label(root, text='Hello world!')
label.pack(pady=20)

button1 = ttk.Button(root, text='Click Me')
button1.pack(pady=10)

button2 = ttk.Button(root, text='Quit', command=root.destroy)
button2.pack(pady=10)

root.mainloop()