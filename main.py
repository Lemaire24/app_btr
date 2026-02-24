from tkinter import Tk
from client import OPCClient
from gui.main_window import MainWindow

root = Tk()
opc = OPCClient()
app = MainWindow(root, opc)
root.mainloop()