# This file defines how to map/handle the patterns
import tkinter as tk
import tkinter.font as tkfont
import math

class Pattern(tk.Frame):

    # Relative bead sizes were obtained from the following website:
    # http://www.firemountaingems.com/resources/encyclobeadia/charts/6903
    # A bead = [x_width, y_height], where the hole is along the y axis.
    _bead_dict = {"size_11_round": [18, 18],
                  "size_11_seed": [18, 15],
                  "size_11_cylinder": [18, 15]}
    curr_bead = "size_11_seed"
    canvas_height = 0
    canvas_width = 0
    curr_color = ""
    canvas = "" #This is set in subclasses! b/c stitches are different
    _images_folder = ""
    _text_width = 0
    _text_height = 0

    def __init__(self, parent, row, col, color, imfldr, bead):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.row = row
        self.col = col
        self._images_folder = imfldr
        self.set_color(color)
        self.curr_bead = bead
        font = tkfont.Font()
        self._text_width = font.measure("100")
        print(self._text_width)
        self._text_height = font.metrics("linespace")
        print(self._text_height)

    #def get_size11(self):
    #    return self.size_11_round
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
    def get_curr_bead(self):
        return self.curr_bead
    def get_bead_dims(self):
        tmp = self.get_curr_bead()
        return self._bead_dict[tmp]
    def get_text_width(self):
        return self._text_width
    def get_text_height(self):
        return self._text_height

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
        #print(items)
        oval_id = items[0]
        self.canvas.itemconfigure(oval_id, fill=self.get_color())

    def save_canvas(self, file_name):
        file_path = self.get_folder() + file_name + ".ps"
        self.canvas.update()
        self.canvas.postscript(file=file_path)
        print("Saved! at:", file_path)

    # Takes: itself, starting x coordinate, starting y coordinate, fill color clr
    # Does: Creates a bead on the canvas, top-left at (x0, y0) (assuming a box
    #   around the bead)
    # Returns: id of the drawn bead
    def bead_points(self, x0, y0, clr):
        bd = self.get_curr_bead()
        if bd == "size_11_round":
            dimens = self.get_bead_dims()
            # Make a round bead, with oval
            x1 = x0 + dimens[0]
            y1 = y0 + dimens[1]
            return self.canvas.create_oval(x0,y0,x1,y1,fill=clr)
        elif bd == "size_11_seed":
            # Make a seed bead, with polygon
            # Note: The y_dim is ASSUMED to be divisible by 3!!
            dimens = self.get_bead_dims()
            width_x = dimens[0]
            height_y = dimens[1]
            short_x = width_x - 4
            short_y = height_y/3
            points = [x0 + 2, y0,
                      x0 + 2 + short_x, y0,
                      x0 + width_x, y0 + short_y,
                      x0 + width_x, y0 + short_y*2,
                      x0 + 2 + short_x, y0 + height_y,
                      x0 + 2, y0 + height_y,
                      x0, y0 + short_y*2,
                      x0, y0 + short_y]
            return self.canvas.create_polygon(points,fill=clr,outline="black",
                                              smooth=True)
        elif bd == "size_11_cylinder":
            # Make a cylinder bead, with rectangle
            # Because from the SIDE, a cylinder bead LOOKS like a rectangle
            dimens = self.get_bead_dims()
            x1 = x0 + dimens[0]
            y1 = y0 + dimens[1]
            return self.canvas.create_rectangle(x0,y0,x1,y1,fill=clr)
        else:
            raise IndexError("No entry in dictionary for current bead: " + bd)


    # SUBCLASSES SHOULD HAVE THE FOLLOWING:

    # def draw_pattern():

class Square(Pattern):

    # A Square stitch basically looks like a grid. Nothing too complicated.
    # For reference:
    # https://www.beadaholique.com/media/wysiwyg/beading-patterns-pngs/Square-Stitch_1000.png

    def __init__(self, parent, row, col, color, imfldr, bead):
        Pattern.__init__(self, parent, row, col, color, imfldr, bead)

        self.scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        #self.scroll_x.grid(row=1, column=0, sticky=tk.W+tk.E)
        self.scroll_y = tk.Scrollbar(self)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        #self.scroll_y.grid(row=0, column=1, sticky=tk.N+tk.S)

        tmp = self.get_bead_dims()
        c_w = tmp[0] * self.get_col() + 2*tmp[0] + self.get_text_width()
        #print(c_w)
        c_h = tmp[1] * self.get_row() + 3*tmp[1] + self.get_text_height()
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
        b = self.get_bead_dims()
        bd_x = b[0]
        bd_y = b[1]
        clr = self.get_color()
        whtspc_x = math.floor(bd_x/2)
        whtspc_y = math.floor(bd_y/2)
        txt_x = self.get_text_width()
        txt_y = self.get_text_height()

        # Drawing the top row of numbers
        y0 = whtspc_y + txt_y
        x_offset = bd_x + txt_x + whtspc_x # This is where "1" would start
        for j in range(2,(c+1),2):
            x0 = (j-1)*bd_x + x_offset
            self.canvas.create_text(x0, y0, anchor=tk.S,
                                    text=j, state=tk.DISABLED)

        # Drawing the beads
        for i in range(1,(r+1)):
            #tmp = []
            y0 = i*bd_y + txt_y
            if i%2 == 0:
                self.canvas.create_text((whtspc_x+txt_x), (y0+whtspc_y),
                                        anchor=tk.E, text=i, state=tk.DISABLED)
            for j in range(0,c):
                # create_oval(x0,y0,x1,y1,...)
                x0 = (j+1)*bd_x + txt_x
                tmp_a = self.bead_points(x0, y0, clr)
                self.canvas.tag_bind(tmp_a, '<B1-Motion>',
                                     self.handle_color)

        self.canvas.config(yscrollcommand=self.scroll_y.set,
                           xscrollcommand=self.scroll_x.set)
        self.scroll_y.config(command=self.canvas.yview)
        self.scroll_x.config(command=self.canvas.xview)
