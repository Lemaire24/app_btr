from tkinter import ttk, messagebox
import tkinter as tk


class DeviceTable:

    def __init__(self, main):

        self.main = main

        self.tab = ttk.Frame(main.notebook)
        main.notebook.add(self.tab, text="Devices")

        self.create_ui()

    def create_ui(self):

        # ===== MAIN CONTAINER =====
        container = ttk.Frame(self.tab)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # ===== TOP BUTTON BAR =====
        button_frame = ttk.Frame(container)
        button_frame.pack(fill="x", pady=(0, 15))

        ttk.Button(
            button_frame,
            text="Editar Devices",
            command=self.main.toggle_edit_mode,
            width=18
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Modo Forzado",
            command=self.main.toggle_force_mode,
            width=18
        ).pack(side="left", padx=5)

        # ===== INPUT TABLE (ARRIBA) =====
        self.tree_inputs = self.create_tree(container, "Entradas")
        self.tree_inputs.pack(fill="x", pady=(0, 20))

        # ===== OUTPUT TABLE (ABAJO) =====
        self.tree_outputs = self.create_tree(container, "Salidas")
        self.tree_outputs.pack(fill="x")

        self.populate()

    def create_tree(self, parent, title):

        frame = ttk.LabelFrame(parent, text=title)
        
        tree = ttk.Treeview(
            frame,
            columns=("Address", "Value", "PLC Tag"),
            show="headings",
            height=8
        )

        tree.heading("Address", text="Address")
        tree.heading("Value", text="Value")
        tree.heading("PLC Tag", text="PLC Tag")

        tree.column("Address", width=120, anchor="center")
        tree.column("Value", width=100, anchor="center")
        tree.column("PLC Tag", width=150, anchor="center")

        tree.pack(fill="x", padx=10, pady=10)
        frame.pack(fill="x")

        tree.bind("<Double-1>", self.edit_cell)

        return tree

    # ================= DATA =================

    def populate(self):

        entradas = ["LS1", "LS2", "LS3", "LS4", "LS5", "DSW"]
        salidas = ["ry1", "ry2", "7S", "PB1", "PB2", "PB3", "PB4", "PB5", "SS0", "SS1"]

        for tag in entradas:
            node_id = f"ns={self.main.namespace_index};s={tag}"
            self.main.nodes[node_id] = tag
            self.main.device_mapping[node_id] = "X0000"
            self.tree_inputs.insert("", "end", iid=node_id,
                                    values=(tag, "N/A", "X0000"))

        for tag in salidas:
            node_id = f"ns={self.main.namespace_index};s={tag}"
            self.main.nodes[node_id] = tag
            self.main.device_mapping[node_id] = "X0000"
            self.tree_outputs.insert("", "end", iid=node_id,
                                     values=(tag, "N/A", "X0000"))

    def update_value(self, node_id, value):

        if node_id in self.tree_inputs.get_children():
            self.tree_inputs.item(node_id,
                                  values=(self.main.nodes[node_id],
                                          value,
                                          self.main.device_mapping[node_id]))

        if node_id in self.tree_outputs.get_children():
            self.tree_outputs.item(node_id,
                                   values=(self.main.nodes[node_id],
                                           value,
                                           self.main.device_mapping[node_id]))

    # ================= EDIT & FORCE =================

    def edit_cell(self, event):

        tree = event.widget
        row_id = tree.identify_row(event.y)
        column = tree.identify_column(event.x)

        if not row_id:
            return

        # ===== EDIT PLC TAG =====
        if column == "#3" and self.main.edit_mode:

            x, y, w, h = tree.bbox(row_id, column)
            entry = ttk.Entry(tree)
            entry.place(x=x, y=y, width=w, height=h)
            entry.insert(0, tree.set(row_id, "PLC Tag"))
            entry.focus()

            def save(e=None):
                new = entry.get()
                tree.set(row_id, "PLC Tag", new)
                self.main.device_mapping[row_id] = new
                entry.destroy()

            entry.bind("<Return>", save)
            entry.bind("<FocusOut>", lambda e: entry.destroy())

        # ===== FORCE OUTPUTS ONLY =====
        elif column == "#2" and self.main.force_mode:

            if tree != self.tree_outputs:
                messagebox.showwarning("Bloqueado", "No se pueden forzar ENTRADAS")
                return

            x, y, w, h = tree.bbox(row_id, column)
            entry = ttk.Entry(tree)
            entry.place(x=x, y=y, width=w, height=h)
            entry.focus()

            def write(e=None):
                try:
                    node = self.main.client.client.get_node(row_id)
                    current_value = node.get_value()
                    raw = entry.get()

                    if isinstance(current_value, bool):
                        new_value = raw.lower() in ["1", "true"]
                    elif isinstance(current_value, int):
                        new_value = int(raw)
                    else:
                        new_value = raw

                    self.main.client.write_value(row_id, new_value)

                except Exception as e:
                    messagebox.showerror("Error", str(e))

                entry.destroy()

            entry.bind("<Return>", write)
            entry.bind("<FocusOut>", lambda e: entry.destroy())