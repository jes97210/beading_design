# Made to work in python3
import tkinter as tk
import Pattern as ptrn
import math
import os

class TopBar(tk.Frame):

    # This is the bar on the top of the window

    _sc = []
    _bd = []

    def __init__(self, parent, stitches, beads):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self._sc = stitches
        self._bd = beads

        self.label_s = tk.Label(self, text="Stitch")
        self.label_s.grid(row=0, column=0)
        self.selectedOption_s = tk.StringVar()
        self.selectedOption_s.set(self._sc[0]) #Default
        self.list_s = tk.OptionMenu(self, self.selectedOption_s, *self._sc)
        self.list_s.grid(row=1, column=0, sticky="S")

        self.label_b = tk.Label(self, text="Bead Type")
        self.label_b.grid(row=0, column=1)
        self.selectedOption_b = tk.StringVar()
        self.selectedOption_b.set(self._bd[0]) #Default
        self.list_b = tk.OptionMenu(self, self.selectedOption_b, *self._bd)
        self.list_b.grid(row=1, column=1, sticky="S")

        self.label_r = tk.Label(self, text="Rows")
        self.label_r.grid(row=0, column=2)
        self.entry_r = tk.Scale(self, from_=1, to=100, orient=tk.HORIZONTAL)
        self.entry_r.grid(row=1, column=2)

        self.label_c = tk.Label(self, text="Columns")
        self.label_c.grid(row=0, column=3)
        self.entry_c = tk.Scale(self, from_=1, to=100, orient=tk.HORIZONTAL)
        self.entry_c.grid(row=1, column=3)

        self.start = tk.Button(self, text="START", command=self.start_go)
        self.start.grid(row=0, column=4, rowspan=2)

    def start_go(self):
        self.parent.top_bar_start(self.selectedOption_s.get(),
                                  self.selectedOption_b.get(),
                                  self.entry_r.get(),
                                  self.entry_c.get())

class OptionBar(tk.Frame):

    # This is the bar on the bottom of the main window.

    def __init__(self, parent, color_set):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.color_bttn = tk.Button(self, text="Colors",
                                command=lambda: self.start_color())
        self.color_bttn.grid(row=1, column=0, columnspan=2)
        self.curr_color = tk.Canvas(self, height=20, width=20)
        self.color_label = tk.Label(self, text="Current Color: ")
        self.color_label.grid(row=0, column=0)
        self.curr_color.grid(row=0, column=1)
        self.color_sqr = self.curr_color.create_rectangle(0,0,20,20,
                                                          fill=color_set)
        self.file_label = tk.Label(self, text="File name: ")
        self.file_label.grid(row=0, column=2)
        self.file_name = tk.Entry(self)
        self.file_name.grid(row=0, column=3)
        self.save_bttn = tk.Button(self, text="Save",
                                   command=lambda: self.save_message())
        self.save_bttn.grid(row=1, column=2, columnspan=2)

    def start_color(self):
        self.colorwin = ColorWindow(self)

    def save_message(self):
        flnm = self.file_name.get()
        self.message_to_pattern(["save",flnm])

    def message_to_pattern(self, msg):
        if msg[0] == "color":
            self.curr_color.itemconfigure(self.color_sqr, fill=msg[1])
        self.parent.message_to_pattern(msg)

class ColorWindow(tk.Toplevel):

    # This is the color window that opens in another window.

    _colors = {"grayscale": ["#000000", "#111111", "#222222", "#333333",
                             "#444444", "#555555", "#666666", "#777777",
                             "#888888", "#999999", "#aaaaaa", "#bbbbbb",
                             "#cccccc", "#dddddd", "#eeeeee", "#ffffff"],
               "basics": ["#ff0000", "#ff9900", "#ffff00", "#00cc00",
                          "#0033cc", "#660099"]}
    _pallets = ["grayscale", "basics"]
    _color_size = 20

    def __init__(self, parent):
        tk.Toplevel.__init__(self,parent)
        self.parent = parent
        self.title("Colors")
        self.make_dropdown()

    def make_dropdown(self):
        self.selectedOption = tk.StringVar()
        self.selectedOption.set(self._pallets[0]) #Default
        self.list1 = tk.OptionMenu(self, self.selectedOption, *self._pallets,
                                   command = self.make_color_buttons)
        self.list1.pack()
        self.make_color_buttons("N/A")
        #self.selectedOption.trace('w', self.make_color_buttons())

    def change_buttons(self):
        self.bttns.destroy()
        self.scroll_x.destroy()
        self.make_color_buttons()

    # Note: event var is NOT used in this func.
    # It's just necessary for the tk.OptionMenu command to work, as an event
    # object is automatically passed on. Pretty annoying, if you ask me!
    def make_color_buttons(self, event):
        try:
            self.bttns.destroy()
            self.scroll_x.destroy()
            self._grid[:] = []
        except AttributeError:
            pass
        curr = self.selectedOption.get()
        col_len = len(self._colors[curr])
        c_s = self._color_size
        c_w = (col_len * c_s) + c_s
        c_h = 2 * c_s

        self.bttns = tk.Canvas(self,scrollregion=(0,0,c_w, c_h), height=c_h,
                               width=c_w)
        self.bttns.pack(fill=tk.X, expand=tk.TRUE)
        self.bttns.configure(highlightthickness=0)

        self.scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        x0 = math.floor(c_s/2)
        y0 = math.floor(c_s/2)
        y1 = y0 + c_s
        i = 0
        for op in self._colors[curr]:
            x1 = x0 + c_s
            tmp_a = self.bttns.create_rectangle(x0,y0,x1,y1,fill=op)
            self.bttns.tag_bind(tmp_a,'<ButtonPress-1>',
                                lambda op=op:self.send_color(op))
            x0 = x1
            i = i + 1

        #self.bttns.bind('<ButtonPress-1>', self.send_color(event))
        self.bttns.config(xscrollcommand=self.scroll_x.set)
        self.scroll_x.config(command=self.bttns.xview)

    def send_color(self, color):
        col = self.determine_color(color.x, color.y)
        if col:
            #aka. determine_color() didn't send back None
            a = color.x
            b = color.y
            print("clicked at ", a, "and", b)
            self.message_to_pattern(["color",col])

    def determine_color(self, x, y):
        true_x = self.bttns.canvasx(x)
        true_y = self.bttns.canvasy(y)
        items = self.bttns.find_closest(true_x,true_y)
        rect_id = items[0]
        return self.bttns.itemcget(rect_id, "fill")

    def message_to_pattern(self, msg):
        self.parent.message_to_pattern(msg)

class MainApp(tk.Tk):

    stitch_choices = ["Square","Not an Option"]
    bead_choices = ["size_11_round", "size_11_seed", "size_11_cylinder"]
    canvasFrame = ""
    _current_color = "#ffffff"
    _background = "#dddddd"
    _images_folder = "BeadingDesignImages/"

    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.title("BeadingDesign")
        self.topBar = TopBar(self, stitches=self.stitch_choices,
                                   beads=self.bead_choices)
        self.topBar.pack(anchor=tk.NW)
        os.makedirs(self._images_folder, exist_ok=True)

    def top_bar_start(self, so, bd, row, col):
        if self.canvasFrame != "":
            self.canvasFrame.destroy()
            self.optionsFrame.destroy()
        print(so)
        print(row)
        print(col)
        if so == self.stitch_choices[0]:
            self.canvasFrame = ptrn.Square(self, row=row, col=col,
                                           color=self._current_color,
                                           imfldr = self._images_folder,
                                           bead = bd)
            self.canvasFrame.pack(fill=tk.BOTH, expand=tk.YES)
            self.optionsFrame = OptionBar(self, self._current_color)
            self.optionsFrame.pack(side=tk.BOTTOM, anchor=tk.E)

    # A message passed through message_to_pattern MUST be an array of len()=2,
    #  with strings. The first says what the message is about (one of "color"
    #  or "save"), and the second has the details (either the color, or the
    #  the file to save to).
    def message_to_pattern(self, message):
        if message[1] == "color":
            self._current_color = message[2]
        self.canvasFrame.message_to_pattern(message)

if __name__ == '__main__':
    app = MainApp(None)
    app.mainloop()
