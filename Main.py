# Made to work in python3
import tkinter as tk
import Pattern as ptrn
import math

class TopBar(tk.Frame):

    _sc = []

    def __init__(self, parent, stitches):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self._sc = stitches

        self.label1 = tk.Label(self, text="Stitch")
        self.label1.grid(row=0, column=0)
        self.selectedOption = tk.StringVar()
        self.selectedOption.set(self._sc[0]) #Default
        self.list1 = tk.OptionMenu(self, self.selectedOption, *self._sc)
        self.list1.grid(row=1, column=0, sticky="S")

        self.label2 = tk.Label(self, text="Rows")
        self.label2.grid(row=0, column=1)
        self.entry2 = tk.Scale(self, from_=1, to=100, orient=tk.HORIZONTAL)
        self.entry2.grid(row=1, column=1)

        self.label3 = tk.Label(self, text="Columns")
        self.label3.grid(row=0, column=2)
        self.entry3 = tk.Scale(self, from_=1, to=100, orient=tk.HORIZONTAL)
        self.entry3.grid(row=1, column=2)

        self.start = tk.Button(self, text="START", command=self.startGo)
        self.start.grid(row=0, column=3, rowspan=2)

    def startGo(self):
        self.parent.topBarStart(self.selectedOption.get(),
                                self.entry2.get(),
                                self.entry3.get())

class OptionBar(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.colors = tk.Button(self, text="colors",
                                command=lambda: self.startColor())
        self.colors.pack()

    def startColor(self):
        self.colorwin = ColorWindow(self)

    def colorMessage(self, color):
        self.parent.colorMessage(color)

class ColorWindow(tk.Toplevel):

    _colors = {"grayscale": ["#000000", "#111111", "#222222", "#333333",
                             "#444444", "#555555", "#666666", "#777777",
                             "#888888", "#999999", "#aaaaaa", "#bbbbbb",
                             "#cccccc", "#dddddd", "#eeeeee", "#ffffff"],
               "Option": []}
    _pallets = ["grayscale", "Option"]
    _color_size = 20

    def __init__(self, parent):
        tk.Toplevel.__init__(self,parent)
        self.parent = parent
        self.title("Colors")
        self.makeDropdown()

    def makeDropdown(self):
        self.selectedOption = tk.StringVar()
        self.selectedOption.set(self._pallets[0]) #Default
        self.list1 = tk.OptionMenu(self, self.selectedOption, *self._pallets)
        self.list1.pack()
        self.makeColorButtons()
        self.selectedOption.trace('w', self.changeButtons())

    def changeButtons(self):
        self.bttns.destroy()
        self.scroll_x.destroy()
        self.makeColorButtons()

    def makeColorButtons(self):
        curr = self.selectedOption.get()
        col_len = len(self._colors[curr])
        c_s = self._color_size
        c_w = (col_len * c_s) + c_s
        c_h = 2 * c_s

        self.bttns = tk.Canvas(self,scrollregion=(0,0,c_w, c_h), height=c_h,
                               width=c_w)
        self.bttns.pack(side=tk.TOP, fill=tk.X, expand=tk.TRUE)
        self.bttns.configure(highlightthickness=0)

        self.scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scroll_x.pack(fill=tk.X)

        x0 = math.floor(c_s/2)
        y0 = math.floor(c_s/2)
        y1 = y0 + c_s
        for op in self._colors[curr]:
            x1 = x0 + c_s
            tmp_a = self.bttns.create_rectangle(x0,y0,x1,y1,fill=op)
            self.bttns.tag_bind(tmp_a,'<ButtonPress-1>',
                                lambda op=op:self.sendColor(op))
            x0 = x1

        self.bttns.config(xscrollcommand=self.scroll_x.set)
        self.scroll_x.config(command=self.bttns.xview)

    def sendColor(self, color):
        self.parent.colorMessage(color)

class MainApp(tk.Tk):

    stitch_choices = ["Square","Not an Option"]
    canvasFrame = ""
    _current_color = "#ffffff"
    _background = "#dddddd"

    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.title("BeadingDesign")
        self.topBar = TopBar(self, stitches=self.stitch_choices)
        self.topBar.pack(anchor=tk.NW)

    def topBarStart(self, so, row, col):
        if self.canvasFrame != "":
            self.canvasFrame.destroy()
            self.optionsFrame.destroy()
        print(so)
        print(row)
        print(col)
        if so == self.stitch_choices[0]:
            self.canvasFrame = ptrn.Square(self, row=row, col=col)
            self.canvasFrame.pack(fill=tk.BOTH, expand=tk.YES)
            self.optionsFrame = OptionBar(self)
            self.optionsFrame.pack(side=tk.BOTTOM)

    def colorMessage(self, color):
        self._current_color = color
        print(self._current_color)

if __name__ == '__main__':
    app = MainApp(None)
    app.mainloop()
