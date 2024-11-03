import tkinter as tk
from tkinter import messagebox, filedialog
import json

class NoteManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NoteManager, cls).__new__(cls)
            cls._instance.notes = []
            cls._instance.observers = []
        return cls._instance

    def add_note(self, name, content):
        self.notes.append({"name": name, "content": content})
        self.notify_observers()

    def delete_note(self, index):
        if 0 <= index < len(self.notes):
            del self.notes[index]
            self.notify_observers()

    def update_note(self, index, name, content):
        if 0 <= index < len(self.notes):
            self.notes[index] = {"name": name, "content": content}
            self.notify_observers()

    def get_notes(self):
        return self.notes

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update()

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.notes, f)

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            self.notes = json.load(f)
        self.notify_observers()

    def search_notes(self, query):
        return [note for note in self.notes if query.lower() in note['name'].lower() or query.lower() in note['content'].lower()]

class NoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Note Taking App")
        self.geometry("700x400")  # Adjusted size for side-by-side layout

        self.note_manager = NoteManager()
        self.note_manager.add_observer(self)

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame for note list
        left_frame = tk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right frame for note editing
        right_frame = tk.Frame(main_frame, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Search bar in left frame
        search_label = tk.Label(left_frame, text="Search Notes:")
        search_label.pack(pady=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        search_entry = tk.Entry(left_frame, textvariable=self.search_var, width=30)
        search_entry.pack()

        # Note list in left frame
        list_label = tk.Label(left_frame, text="Notes:")
        list_label.pack(pady=(10, 5))
        self.note_listbox = tk.Listbox(left_frame, width=40, height=15)
        self.note_listbox.pack(fill=tk.BOTH, expand=True)
        self.note_listbox.bind('<<ListboxSelect>>', self.on_select)

        # Note editing in right frame
        self.name_label = tk.Label(right_frame, text="Note Name:")
        self.name_label.pack(pady=(0, 5))
        self.name_entry = tk.Entry(right_frame, width=50)
        self.name_entry.pack()

        self.content_label = tk.Label(right_frame, text="Note Content:")
        self.content_label.pack(pady=(10, 5))
        self.content_entry = tk.Text(right_frame, height=10, width=50)
        self.content_entry.pack()

        # Buttons in right frame
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=10)

        create_button = tk.Button(button_frame, text="Create", command=self.create_note)
        create_button.grid(row=0, column=0, padx=5)

        update_button = tk.Button(button_frame, text="Update", command=self.update_note)
        update_button.grid(row=0, column=1, padx=5)

        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_note)
        delete_button.grid(row=0, column=2, padx=5)

        save_button = tk.Button(button_frame, text="Save", command=self.save_notes)
        save_button.grid(row=1, column=0, padx=5, pady=5)

        load_button = tk.Button(button_frame, text="Load", command=self.load_notes)
        load_button.grid(row=1, column=1, padx=5, pady=5)

        self.update()

    def create_note(self):
        name = self.name_entry.get().strip()
        content = self.content_entry.get("1.0", tk.END).strip()
        if name and content:
            self.note_manager.add_note(name, content)
            self.name_entry.delete(0, tk.END)
            self.content_entry.delete("1.0", tk.END)
        else:
            messagebox.showwarning("Empty Fields", "Please enter both a name and content for the note.")

    def update_note(self):
        selected_indices = self.note_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            name = self.name_entry.get().strip()
            content = self.content_entry.get("1.0", tk.END).strip()
            if name and content:
                self.note_manager.update_note(index, name, content)
                self.name_entry.delete(0, tk.END)
                self.content_entry.delete("1.0", tk.END)
            else:
                messagebox.showwarning("Empty Fields", "Please enter both a name and content for the note.")
        else:
            messagebox.showwarning("No Selection", "Please select a note to update.")

    def delete_note(self):
        selected_indices = self.note_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            self.note_manager.delete_note(index)
        else:
            messagebox.showwarning("No Selection", "Please select a note to delete.")

    def on_select(self, event):
        selected_indices = self.note_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            note = self.note_manager.get_notes()[index]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, note["name"])
            self.content_entry.delete("1.0", tk.END)
            self.content_entry.insert(tk.END, note["content"])

    def update(self):
        self.update_list()

    def update_list(self, *args):
        self.note_listbox.delete(0, tk.END)
        query = self.search_var.get()
        notes = self.note_manager.search_notes(query) if query else self.note_manager.get_notes()
        for note in notes:
            self.note_listbox.insert(tk.END, note['name'])

    def save_notes(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            self.note_manager.save_to_file(filename)
            messagebox.showinfo("Save Successful", "Notes have been saved to file.")

    def load_notes(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            try:
                self.note_manager.load_from_file(filename)
                messagebox.showinfo("Load Successful", "Notes have been loaded from file.")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid file format. Please select a valid JSON file.")
            except FileNotFoundError:
                messagebox.showerror("Error", "File not found.")

if __name__ == "__main__":
    app = NoteApp()
    app.mainloop()