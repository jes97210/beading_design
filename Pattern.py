# This file defines how to map/handle the patterns
import tkinter as tk
import math

class Pattern(tk.Frame):

    # Relative bead sizes were obtained from the following website:
    # http://www.firemountaingems.com/resources/encyclobeadia/charts/6903
    # A bead = [x_width, y_height], where the hole is along the y axis.
    size_11_round = [18, 18]
    canvas_height = 0
    canvas_width = 0
    curr_color = ""
    canvas = "" #This is set in subclasses! b/c stitches are different
    _images_folder = ""

    def __init__(self, parent, row, col, color, imfldr):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.row = row
        self.col = col
        self._images_folder = imfldr
        self.set_color(color)

    def get_size11(self):
        return self.size_11_round
    def get_parent(self):
        return self.parent
    def get_row(self):
        return self.row
    def get_col(self):
        return self.col
    def set_color(self, color):
        self.curr_color = color
    def get_color(self):
        return self.curr_color
    def get_folder(self):
        return self._images_folder

    def message_to_pattern(self, m):
        m_type = m[0]
        if m_type == "color":
            #A new curr_color has been sent
            self.set_color(m[1])
        elif m_type == "save":
            #Saving the canvas
            self.save_canvas(m[1])
        else:
            print("bad message sent!")

    def handle_color(self, event):
        true_x = self.canvas.canvasx(event.x)
        true_y = self.canvas.canvasy(event.y)
        items = self.canvas.find_closest(true_x, true_y)
        print(items)
        oval_id = items[0]
        self.canvas.itemconfigure(oval_id, fill=self.get_color())

    def save_canvas(self, file_name):
        file_path = self.get_folder() + file_name + ".ps"
        self.canvas.update()
        self.canvas.postscript(file=file_path)
        print("Saved! at:", file_path)

    # SUBCLASSES SHOULD HAVE THE FOLLOWING:

    # def draw_pattern():

class Square(Pattern):

    # A Square stitch basically looks like a grid. Nothing too complicated.
    # For reference:
    # https://www.beadaholique.com/media/wysiwyg/beading-patterns-pngs/Square-Stitch_1000.png

    def __init__(self, parent, row, col, color, imfldr):
        Pattern.__init__(self, parent, row, col, color, imfldr)

        self.scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        #self.scroll_x.grid(row=1, column=0, sticky=tk.W+tk.E)
        self.scroll_y = tk.Scrollbar(self)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        #self.scroll_y.grid(row=0, column=1, sticky=tk.N+tk.S)

        tmp = self.get_size11()
        c_w = tmp[0] * self.get_col() + 3*tmp[0]
        print(c_w)
        c_h = tmp[1] * self.get_row() + 3*tmp[1]
        self.canvas = tk.Canvas(self,scrollregion=(0,0,c_w, c_h))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        #self.canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        # This makes sure that beads aren't cut off at the edges.
        self.canvas.configure(highlightthickness=0,
                              borderwidth=0)

        self.draw_pattern()

    def draw_pattern(self):
        r = self.get_row()
        c = self.get_col()
        b = self.get_size11()
        clr = self.get_color()
        whtspc_x = math.floor(b[0]/2)
        whtspc_y = math.floor(b[1]/2)

        # Drawing the top row of numbers
        y0 = whtspc_y
        for j in range(2,(c+1),2):
            x0 = j*b[0] + whtspc_x
            self.canvas.create_text(x0, y0, anchor=tk.NW,
                                    text=j, state=tk.DISABLED)

        # Drawing the beads
        for i in range(1,(r+1)):
            #tmp = []
            y0 = i*b[1] + whtspc_y
            if i%2 == 0:
                self.canvas.create_text(whtspc_x, y0, anchor=tk.NW,
                                        text=i, state=tk.DISABLED)
            for j in range(1,(c+1)):
                # create_oval(x0,y0,x1,y1,...)
                x0 = j*b[0] + whtspc_x
                x1 = x0 + b[0]
                y1 = y0 + b[1]
                tmp_a = self.canvas.create_oval(x0,y0,x1,y1,fill=clr)
                self.canvas.tag_bind(tmp_a, '<B1-Motion>',
                                     self.handle_color)

        self.canvas.config(yscrollcommand=self.scroll_y.set,
                           xscrollcommand=self.scroll_x.set)
        self.scroll_y.config(command=self.canvas.yview)
        self.scroll_x.config(command=self.canvas.xview)
