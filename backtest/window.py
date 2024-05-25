import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class Window:
    def __init__(self, title):
        self.root = tk.Tk()
        self.root.title("Matplotlib with Tabs")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=1)

    def addTab(self, tabName, fig1, ax1, fig2=None, ax2=None):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=tabName)

        if fig2 and ax2:
            fig2.set_size_inches(12, 3)

            zp = ZoomPan(ax1, ax2)
            fig1.canvas.mpl_connect("scroll_event", zp.zoom_factory(1.1))
            zp.pan_factory()

            fig2.canvas.mpl_connect("scroll_event", zp.zoom_factory(1.1))
            zp.pan_factory()

            canvas1 = FigureCanvasTkAgg(fig1, master=tab)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=1)

            canvas2 = FigureCanvasTkAgg(fig2, master=tab)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        else:
            zp = ZoomPan(ax1)
            fig1.canvas.mpl_connect("scroll_event", zp.zoom_factory(1.1))
            zp.pan_factory()

            canvas1 = FigureCanvasTkAgg(fig1, master=tab)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        reset_button = tk.Button(
            tab, text="Reset", command=lambda: self.reset_plot(ax1, ax2, zp)
        )
        reset_button.pack()

    def on_closing(self):
        plt.close("all")
        self.root.destroy()

    def reset_plot(self, ax1, ax2, zp):
        ax1.set_xlim(zp.init_xlim1)
        ax1.set_ylim(zp.init_ylim1)
        ax1.figure.canvas.draw()
        if ax2:
            ax2.set_xlim(zp.init_xlim2)
            ax2.set_ylim(zp.init_ylim2)
            ax2.figure.canvas.draw()

    def show(self):
        self.root.mainloop()


class ZoomPan:
    def __init__(self, ax1, ax2=None):
        self.ax1 = ax1
        self.ax2 = ax2
        self.press = None
        self.init_xlim1 = self.ax1.get_xlim()
        self.init_ylim1 = self.ax1.get_ylim()
        if self.ax2:
            self.init_xlim2 = self.ax2.get_xlim()
            self.init_ylim2 = self.ax2.get_ylim()
        self.cur_xlim1 = self.init_xlim1
        self.cur_ylim1 = self.init_ylim1
        if self.ax2:
            self.cur_xlim2 = self.init_xlim2
            self.cur_ylim2 = self.init_ylim2
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None

    def zoom_factory(self, base_scale=1.1):
        def zoom(event):
            cur_xlim1 = self.ax1.get_xlim()
            cur_ylim1 = self.ax1.get_ylim()
            if self.ax2:
                cur_xlim2 = self.ax2.get_xlim()
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

            new_width1 = (cur_xlim1[1] - cur_xlim1[0]) * scale_factor
            new_height1 = (cur_ylim1[1] - cur_ylim1[0]) * scale_factor

            if self.ax2:
                new_width2 = (cur_xlim2[1] - cur_xlim2[0]) * scale_factor

            relx1 = (cur_xlim1[1] - xdata) / (cur_xlim1[1] - cur_xlim1[0])
            rely1 = (cur_ylim1[1] - ydata) / (cur_ylim1[1] - cur_ylim1[0])

            self.ax1.set_xlim(
                [xdata - new_width1 * (1 - relx1), xdata + new_width1 * (relx1)]
            )
            self.ax1.set_ylim(
                [ydata - new_height1 * (1 - rely1), ydata + new_height1 * (rely1)]
            )

            if self.ax2:
                relx2 = (cur_xlim2[1] - xdata) / (cur_xlim2[1] - cur_xlim2[0])
                self.ax2.set_xlim(
                    [xdata - new_width2 * (1 - relx2), xdata + new_width2 * (relx2)]
                )

            self.ax1.figure.canvas.draw()
            if self.ax2:
                self.ax2.figure.canvas.draw()

        return zoom

    def pan_factory(self):
        def on_press(event):
            if event.inaxes != self.ax1 and (self.ax2 and event.inaxes != self.ax2):
                return
            self.cur_xlim1 = self.ax1.get_xlim()
            self.cur_ylim1 = self.ax1.get_ylim()
            if self.ax2:
                self.cur_xlim2 = self.ax2.get_xlim()
            self.press = self.x0, self.y0, event.xdata, event.ydata

        def on_release(event):
            self.press = None
            self.ax1.figure.canvas.draw()
            if self.ax2:
                self.ax2.figure.canvas.draw()

        def on_motion(event):
            if self.press is None:
                return
            if event.inaxes != self.ax1 and (self.ax2 and event.inaxes != self.ax2):
                return
            x0, y0, xpress, ypress = self.press
            dx = event.xdata - xpress

            self.ax1.set_xlim(self.cur_xlim1[0] - dx, self.cur_xlim1[1] - dx)
            self.ax1.set_ylim(self.cur_ylim1[0], self.cur_ylim1[1])

            if self.ax2:
                self.ax2.set_xlim(self.cur_xlim2[0] - dx, self.cur_xlim2[1] - dx)
                self.ax2.set_ylim(self.cur_ylim2[0], self.cur_ylim2[1])

            self.ax1.figure.canvas.draw()
            if self.ax2:
                self.ax2.figure.canvas.draw()

        self.ax1.figure.canvas.mpl_connect("button_press_event", on_press)
        self.ax1.figure.canvas.mpl_connect("button_release_event", on_release)
        self.ax1.figure.canvas.mpl_connect("motion_notify_event", on_motion)

        if self.ax2:
            self.ax2.figure.canvas.mpl_connect("button_press_event", on_press)
            self.ax2.figure.canvas.mpl_connect("button_release_event", on_release)
            self.ax2.figure.canvas.mpl_connect("motion_notify_event", on_motion)


def create_plot():
    fig = Figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax.plot(x, y)

    return fig, ax


if __name__ == "__main__":
    window = Window("Matplotlib with Tabs")

    fig1, ax1 = create_plot()
    window.addTab("Plot 1", fig1, ax1)

    fig2, ax2 = create_plot()
    fig22, ax22 = create_plot()
    window.addTab("Plot 2", fig2, ax2, fig22, ax22)

    fig3, ax3 = create_plot()
    window.addTab("Plot 3", fig3, ax3)

    window.show()
