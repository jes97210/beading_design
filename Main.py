# Made to work in python3
import tkinter as tk
import Pattern as ptrn
import math
import os

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

        self.start = tk.Button(self, text="START", command=self.start_go)
        self.start.grid(row=0, column=3, rowspan=2)

    def start_go(self):
        self.parent.top_bar_start(self.selectedOption.get(),
                                self.entry2.get(),
                                self.entry3.get())

class OptionBar(tk.Frame):

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
        #self._grid[:] = []
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
    canvasFrame = ""
    _current_color = "#ffffff"
    _background = "#dddddd"
    _images_folder = "BeadingDesignImages/"

    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.title("BeadingDesign")
        self.topBar = TopBar(self, stitches=self.stitch_choices)
        self.topBar.pack(anchor=tk.NW)
        os.makedirs(self._images_folder, exist_ok=True)

    def top_bar_start(self, so, row, col):
        if self.canvasFrame != "":
            self.canvasFrame.destroy()
            self.optionsFrame.destroy()
        print(so)
        print(row)
        print(col)
        if so == self.stitch_choices[0]:
            self.canvasFrame = ptrn.Square(self, row=row, col=col,
                                           color=self._current_color,
                                           imfldr = self._images_folder)
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
