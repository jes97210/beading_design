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
    canvas = ""
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

    # This is called in a subclass. They determine the width(wid) and
    #   height(hig) appropriate for the stitch in their __init__().
    def start_canvas(self, wid, hig):
        self.scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y = tk.Scrollbar(self)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(self,scrollregion=(0,0,wid, hig))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        # This makes sure that beads aren't cut off at the edges.
        self.canvas.configure(highlightthickness=0, borderwidth=0)

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

    # Takes: self, point (x0,y0), rotation rtn (ASSUMED in degrees), array of
    #        points of the bead
    # Does: Rotates the array of points around (x0,y0).
    # Returns: array of rotated and shifted points
    # REMEMBER: points is NOT an array of tuples, just an array where the even
    #  indices have x coordinates, and the odd indicies have y coordinates.
    # ALSO: A tkinter canvas has (0,0) at the top left. SO, the canvas is
    #  quadrant I but it oriented more like quadrant II. Just incase there's
    #  confusion when reading this...
    def rotate_around_point(self, x0, y0, rtn, points):
        a = rtn > 90
        b = rtn < (-90)
        c = rtn < 0
        lowest_x = x0
        lowest_y = y0
        if a or b:
            if a:
                tmp = math.floor(rtn/90)
            else:
                tmp = math.ceil(rtn/90)
            rtn = rtn - (90*tmp)
        # Perform the rotation
        rtn_rad = math.radians(rtn)
        cos_rtn = math.cos(rtn_rad)
        sin_rtn = math.sin(rtn_rad)
        for p in range(0,len(points),2):
            tmp_x = points[p]
            tmp_y = points[p+1]
            tmp_x1 = cos_rtn*(tmp_x-x0) - sin_rtn*(tmp_y-y0) + x0
            if tmp_x1 < lowest_x:
                lowest_x = tmp_x1
            points[p] = tmp_x1
            tmp_y1 = sin_rtn*(tmp_x-x0) + cos_rtn*(tmp_y-y0) + y0
            if tmp_y1 < lowest_y:
                lowest_y = tmp_y1
            points[p+1] = tmp_y1
        return points

    # Takes: self, starting coordinates x0 and y0
    # Returns: set of points for a round bead
    def calculate_round_points(self, x0, y0):
        dimens = self.get_bead_dims()
        x1 = x0 + dimens[0]
        y1 = y0 + dimens[1]
        return [x0, y0, x1, y1]

    # Takes: self, starting coordinates x0 and y0
    # Returns: set of points for a seed bead
    def calculate_seed_points(self, x0, y0):
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
        return points

    # Takes: self, starting coordinates x0 and y0
    # Returns: set of points for a cylinder bead
    def calculate_cylinder_points(self, x0, y0):
        dimens = self.get_bead_dims()
        width_x = dimens[0]
        height_y = dimens[1]
        points = [x0, y0,
                  x0 + width_x, y0,
                  x0 + width_x, y0 + height_y,
                  x0, y0 + height_y]
        return points

    # Takes: self, starting x coordinate, starting y coordinate, fill color clr,
    #        rotation rtn
    # Does: Creates a bead on the canvas, top-left at (x0, y0) (assuming a box
    #       around the bead)
    # Returns: id of the drawn bead
    def draw_bead_points(self, x0, y0, clr, rtn):
        bd = self.get_curr_bead()
        dimens = self.get_bead_dims()
        width_x = dimens[0]
        height_y = dimens[1]
        if bd == "size_11_round":
            # Make a round bead, with oval
            # A circle is a circle, regardless of how it's rotated, thus rtn is
            #  not used here.
            points = self.calculate_round_points(x0, y0)
            return self.canvas.create_oval(points,fill=clr)
        elif bd == "size_11_seed":
            # Make a seed bead, with polygon
            # Note: The y_dim is ASSUMED to be divisible by 3!!
            points = self.calculate_seed_points(x0, y0)
            if not rtn == 0:
                # Get the rotation for the bead
                cent_x = x0 + width_x/2
                cent_y = y0 + height_y/2
                points = self.rotate_around_point(cent_x, cent_y, rtn, points)
            return self.canvas.create_polygon(points,fill=clr,outline="black",
                                              smooth=True)
        elif bd == "size_11_cylinder":
            # Make a cylinder bead, with rectangle
            # Because from the SIDE, a cylinder bead LOOKS like a rectangle
            points = self.calculate_cylinder_points(x0, y0)
            if not rtn == 0:
                # Get the rotation for the bead
                cent_x = x0 + width_x/2
                cent_y = y0 + height_y/2
                points = self.rotate_around_point(cent_x, cent_y, rtn, points)
            return self.canvas.create_polygon(points,fill=clr,outline="black")
        else:
            raise IndexError("No entry in dictionary for current bead: " + bd)


    # SUBCLASSES SHOULD HAVE THE FOLLOWING:

    # def draw_pattern():

class Square(Pattern):

    # A Square stitch basically looks like a grid. Nothing too complicated.
    # For reference:
    # https://tinyurl.com/y8xsffkp
    def __init__(self, parent, row, col, color, imfldr, bead):
        Pattern.__init__(self, parent, row, col, color, imfldr, bead)

        tmp = self.get_bead_dims()
        c_w = tmp[0] * self.get_col() + 2*tmp[0] + self.get_text_width()
        c_h = tmp[1] * self.get_row() + 3*tmp[1] + self.get_text_height()
        self.start_canvas(c_w, c_h)

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
                x0 = (j+1)*bd_x + txt_x
                tmp_a = self.draw_bead_points(x0, y0, clr, 0)
                self.canvas.tag_bind(tmp_a, '<B1-Motion>', self.handle_color)

        self.canvas.config(yscrollcommand=self.scroll_y.set,
                           xscrollcommand=self.scroll_x.set)
        self.scroll_y.config(command=self.canvas.yview)
        self.scroll_x.config(command=self.canvas.xview)

class Brick(Pattern):

    # A Brick stitch looks like a grid, with each row being offset by half a
    #   bead. Very similar to Peyote stitch.
    # For reference:
    # https://tinyurl.com/y9vxge36
    # ALSO, for NOW, each row is assumed to have the same number of beads.
    def __init__(self, parent, row, col, color, imfldr, bead):
        Pattern.__init__(self, parent, row, col, color, imfldr, bead)

        tmp = self.get_bead_dims()
        c_w = tmp[0] * self.get_col() + 3*tmp[0] + self.get_text_width()
        c_h = tmp[1] * self.get_row() + 3*tmp[1] + self.get_text_height()
        self.start_canvas(c_w, c_h)

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
            y0 = i*bd_y + txt_y
            if i%2 == 0:
                self.canvas.create_text((whtspc_x+txt_x), (y0+whtspc_y),
                                        anchor=tk.E, text=i, state=tk.DISABLED)
            for j in range(0,c):
                if i%2==0:
                    x0 = (j+1)*bd_x + txt_x + whtspc_x
                else:
                    x0 = (j+1)*bd_x + txt_x
                tmp_a = self.draw_bead_points(x0, y0, clr, 0)
                self.canvas.tag_bind(tmp_a, '<B1-Motion>', self.handle_color)

        self.canvas.config(yscrollcommand=self.scroll_y.set,
                           xscrollcommand=self.scroll_x.set)
        self.scroll_y.config(command=self.canvas.yview)
        self.scroll_x.config(command=self.canvas.xview)

class Herringbone(Pattern):

    # A Herringbone stitch looks like a grid, but each bead has a slight tilt.
    # For reference:
    # https://tinyurl.com/y6u3k3ju
    # NOTE: Herringbone stitch NEEDS an even number of columns!

    # This accounts for the tilt.
    _rotation_odd = 20
    _rotation_even = -20
    _offset_x = 0
    _offset_y = 0

    def __init__(self, parent, row, col, color, imfldr, bead):

        if not col%2==0:
            raise ValueError("Herringbone needs an even number of columns")
        else:
            Pattern.__init__(self, parent, row, col, color, imfldr, bead)

            tmp = self.get_bead_dims()
            print("Old bead space (hori, vert): ")
            print(tmp[0])
            print(tmp[1])
            tmp = self.calculate_offset(tmp)
            print("New bead space (hori, vert): ")
            print(tmp[0])
            print(tmp[1])
            c_w = tmp[0] * self.get_col() + 2*tmp[0] + self.get_text_width()
            c_h = tmp[1] * self.get_row() + 3*tmp[1] + self.get_text_height()
            self._offset_x = tmp[0]
            self._offset_y = tmp[1]
            self.start_canvas(c_w, c_h)

            self.draw_pattern()

    # Takes: An array with bead dimmensions [width, height]
    # Does: Calculates how much "larger" a bead becomes on the canvas with
    #       rotation. This is necessary so that they don't overlap each other
    #       on the canvas.
    # Returns: An array of the adjusted [width, height]
    def calculate_offset(self, bead_dims):
        points = [0,0,
                  bead_dims[0], 0,
                  bead_dims[0], bead_dims[1],
                  0, bead_dims[1]]
        cent_x = bead_dims[0]/2
        cent_y = bead_dims[1]/2
        points = self.rotate_around_point(cent_x, cent_y, self._rotation_odd,
                                          points)

        lowest_x = points[6]
        lowest_y = points[1]
        for p in range(0,len(points),2):
            points[p] = points[p] - lowest_x
            points[p+1] = points[p+1] - lowest_y
        print(points)

        d_tmp = self.get_curr_bead()
        if "seed" in d_tmp:
            new_x = bead_dims[0]
        elif "round" in d_tmp:
            return [bead_dims[0], bead_dims[1]]
        else:
            new_x = points[2]
        print("new_x: ")
        print(new_x)
        # Calculate where the top corner drops down to
        # aka. the intercept of the first point x on the line on the bottom.
        x1, y1 = points[4], points[5]
        x2, y2 = points[6], points[7]
        m = (y1 - y2)/(x1 - x2)
        b = y1 - m*x1
        new_y = m*points[0] + b
        print("new_y: ")
        print(new_y)
        return [new_x, new_y]


    def draw_pattern(self):
        r = self.get_row()
        c = self.get_col()
        b = self.get_bead_dims()
        bd_x = b[0]
        bd_y = b[1]
        offset_bd_x = self._offset_x
        offset_bd_y = self._offset_y
        clr = self.get_color()
        whtspc_x = math.floor(bd_x/2)
        whtspc_y = math.floor(bd_y/2)
        txt_x = self.get_text_width()
        txt_y = self.get_text_height()

        # Drawing the top row of numbers
        y0 = whtspc_y + txt_y
        x_offset = offset_bd_x + txt_x + whtspc_x # This is where "1" would start
        for j in range(2,(c+1),2):
            x0 = (j-1)*offset_bd_x + x_offset
            self.canvas.create_text(x0, y0, anchor=tk.S,
                                    text=j, state=tk.DISABLED)

        # Drawing the beads
        for i in range(1,(r+1)):
            y0 = i*offset_bd_y + txt_y
            if i%2 == 0:
                self.canvas.create_text((whtspc_x+txt_x), (y0+whtspc_y),
                                        anchor=tk.E, text=i, state=tk.DISABLED)
            for j in range(0,c):
                if j%2 == 0:
                    rota = self._rotation_odd
                else:
                    rota = self._rotation_even
                x0 = (j+1)*offset_bd_x + txt_x
                tmp_a = self.draw_bead_points(x0, y0, clr, rota)
                self.canvas.tag_bind(tmp_a, '<B1-Motion>', self.handle_color)

        self.canvas.config(yscrollcommand=self.scroll_y.set,
                           xscrollcommand=self.scroll_x.set)
        self.scroll_y.config(command=self.canvas.yview)
        self.scroll_x.config(command=self.canvas.xview)
