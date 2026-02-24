import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class GeneralPanel:

    def __init__(self, main):

        self.main = main

        self.tab = ttk.Frame(main.notebook)
        main.notebook.add(self.tab, text="General")

        self.setup_ui()

    def setup_ui(self):

        # ===== CANVAS =====
        self.canvas = tk.Canvas(self.tab, width=1100, height=700)
        self.canvas.pack(fill="both", expand=True)

        # ===== IMAGEN FONDO =====
        bg = Image.open("resources/panel.png")
        self.bg_img = ImageTk.PhotoImage(bg)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)

        # ===== BOTÓN PB1 =====
        self.load_button(
            tag="PB1",
            x=450,
            y=550,
            normal_img="resources/rotatory_left.png",
            pressed_img="resources/rotatory_right.png"
        )

    # ==================================================
    # BOTÓN GENÉRICO
    # ==================================================

    def load_button(self, tag, x, y, normal_img, pressed_img):

        normal = ImageTk.PhotoImage(Image.open(normal_img))
        pressed = ImageTk.PhotoImage(Image.open(pressed_img))

        setattr(self, f"{tag}_normal", normal)
        setattr(self, f"{tag}_pressed", pressed)

        button = self.canvas.create_image(x, y, image=normal)

        self.canvas.tag_bind(
            button,
            "<ButtonPress-1>",
            lambda e: self.button_press(tag, button)
        )

        self.canvas.tag_bind(
            button,
            "<ButtonRelease-1>",
            lambda e: self.button_release(tag, button)
        )

    # ==================================================
    # EVENTOS
    # ==================================================

    def button_press(self, tag, button_id):

        self.canvas.itemconfig(
            button_id,
            image=getattr(self, f"{tag}_pressed")
        )

        node_id = f"ns={self.main.namespace_index};s={tag}"
        self.main.client.write_value(node_id, True)

    def button_release(self, tag, button_id):

        self.canvas.itemconfig(
            button_id,
            image=getattr(self, f"{tag}_normal")
        )

        node_id = f"ns={self.main.namespace_index};s={tag}"
        self.main.client.write_value(node_id, False)