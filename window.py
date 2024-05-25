import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from matplotlib.widgets import Cursor


class Window:
    def __init__(self, ax):
        self.ax = ax
        self.press = None
        self.cur_xlim = self.ax.get_xlim()
        self.cur_ylim = self.ax.get_ylim()
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None

    def zoom_factory(self, base_scale=1.1):
        def zoom(event):
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()
            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location
            if event.button == "up":
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == "down":
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            self.ax.set_xlim(
                [xdata - new_width * (1 - relx), xdata + new_width * (relx)]
            )
            self.ax.set_ylim(
                [ydata - new_height * (1 - rely), ydata + new_height * (rely)]
            )
            self.ax.figure.canvas.draw()

        return zoom

    def pan_factory(self):
        def on_press(event):
            if event.inaxes != self.ax:
                return
            self.cur_xlim = self.ax.get_xlim()
            self.cur_ylim = self.ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata

        def on_release(event):
            self.press = None
            self.ax.figure.canvas.draw()

        def on_motion(event):
            if self.press is None:
                return
            if event.inaxes != self.ax:
                return
            x0, y0, xpress, ypress = self.press
            dx = event.xdata - xpress
            dy = event.ydata - ypress
            self.ax.set_xlim(self.cur_xlim[0] - dx, self.cur_xlim[1] - dx)
            self.ax.set_ylim(self.cur_ylim[0] - dy, self.cur_ylim[1] - dy)
            self.ax.figure.canvas.draw()

        self.ax.figure.canvas.mpl_connect("button_press_event", on_press)
        self.ax.figure.canvas.mpl_connect("button_release_event", on_release)
        self.ax.figure.canvas.mpl_connect("motion_notify_event", on_motion)


def create_plot(tab):
    fig = Figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax.plot(x, y)
    # cursor = Cursor(ax, useblit=True, color="red", linewidth=1)

    zp = Window(ax)
    fig.canvas.mpl_connect("scroll_event", zp.zoom_factory(1.1))
    zp.pan_factory()

    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)


def on_closing():
    plt.close("all")
    root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Matplotlib with Tabs")
    root.protocol("WM_DELETE_WINDOW", on_closing)

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=1)

    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)

    notebook.add(tab1, text="Plot 1")
    notebook.add(tab2, text="Plot 2")
    notebook.add(tab3, text="Plot 3")

    create_plot(tab1)
    create_plot(tab2)
    create_plot(tab3)

    root.mainloop()
