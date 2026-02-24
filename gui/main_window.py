import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from .general_panel import GeneralPanel
from .device_table import DeviceTable


class MainWindow:

    def __init__(self, root, opc_client):
        self.root = root
        self.client = opc_client

        self.root.title("Industrial OPC UA Panel")
        self.root.geometry("1100x750")

        self.namespace_index = 2
        self.nodes = {}
        self.device_mapping = {}
        self.edit_mode = False
        self.force_mode = False

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Tabs
        self.general_panel = GeneralPanel(self)
        self.config_tab = self.create_config_tab()
        self.device_table = DeviceTable(self)

    # ==================================================
    # CONFIG TAB
    # ==================================================
    def create_config_tab(self):

        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Configuración")

        frame = ttk.LabelFrame(tab, text="Conexión OPC UA")
        frame.pack(pady=30, padx=30, fill="x")

        ttk.Label(frame, text="IP Address:").grid(row=0, column=0, pady=5)
        self.entry_ip = ttk.Entry(frame)
        self.entry_ip.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Port:").grid(row=1, column=0, pady=5)
        self.entry_port = ttk.Entry(frame)
        self.entry_port.insert(0, "4840")
        self.entry_port.grid(row=1, column=1, pady=5)

        ttk.Button(frame, text="Conectar", command=self.start_connection).grid(row=2, column=0, pady=10)
        ttk.Button(frame, text="Desconectar", command=self.stop_connection).grid(row=2, column=1, pady=10)

        return tab

    # ==================================================
    # MODOS
    # ==================================================
    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode

    def toggle_force_mode(self):
        self.force_mode = not self.force_mode

    # ==================================================
    # CONEXIÓN
    # ==================================================
    def start_connection(self):

        ip = self.entry_ip.get().strip()
        port = self.entry_port.get().strip()

        if not ip or not port:
            messagebox.showerror("Error", "IP y Puerto requeridos")
            return

        endpoint = f"opc.tcp://{ip}:{port}"
        self.client.set_endpoint(endpoint)

        if self.client.connect():

            self.general_panel.update_status(True)

            namespaces = self.client.get_namespaces()
            for i, ns in enumerate(namespaces):
                if "KV" in ns or "keyence" in ns.lower():
                    self.namespace_index = i

            self.client.create_subscription(self.subscription_callback)

            for node_id in self.nodes.keys():
                self.client.subscribe(node_id)

        else:
            messagebox.showerror("Error", "Conexión fallida")

    def stop_connection(self):
        self.client.disconnect()
        self.general_panel.update_status(False)

    # ==================================================
    # CALLBACK
    # ==================================================
    def subscription_callback(self, node, value):
        node_id = node.nodeid.to_string()
        self.root.after(0, self.update_value, node_id, value)

    def update_value(self, node_id, value):

        self.device_table.update_value(node_id, value)

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        self.general_panel.update_visual(node_id, value)