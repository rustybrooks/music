# -----------------------------------------------------------------------------
# Dial widget that shows a turnable knob for setting an angle.
#
import math
import tkinter


# -----------------------------------------------------------------------------
# Radius is in any Tk-acceptable format.
# Command callback takes an angle argument (degrees).
#
class Dial:
    def __init__(
        self, parent, radius='.5i',
        command=None, press_command=None, release_command=None,
        initAngle=0.0,
        zeroAxis='x',
        rotDir='clockwise',
        fill=None,
        outline='black',
        line='black',
        label='',
        bg=None,
    ):


        self.command = command
        self.press_command = press_command
        self.release_command = release_command
        self.radius = parent.winfo_pixels(radius)
        self.bump_size = .2 * self.radius
        rpb = self.radius + self.bump_size
        self.center_xy = (rpb, rpb)
        self.drag_from_angle = None

        s = int(2 * (self.radius + self.bump_size))
        c = tkinter.Canvas(parent, width=s, height=s, bg=bg, border=0, highlightbackground=bg)
        cx, cy = self.center_xy
        r = self.radius
        kw = {}
        if fill is not None:
            kw['fill'] = fill
        if outline is not None:
            kw['outline'] = outline
        self.main = c.create_oval(cx-r, cy-r, cx+r, cy+r, **kw)

        self.mid = c.create_oval(cx-r//2, cy-r//2, cx+r//2, cy+r//2, fill='white')
        c.tag_bind(self.mid, '<ButtonPress-1>', self.mid_press_cb)
        c.tag_bind(self.mid, '<ButtonRelease-1>', self.mid_release_cb)

        if label:
            c.create_text(cx, cy, text=label, anchor='c', fill='black')

        bs = self.bump_size
        kw = {'width': bs}
        if line is not None:
            kw['fill'] = line
        id = c.create_line(cx+r//5, cy, cx+r + bs, cy, **kw)
        self.line_id = id
        self.canvas = c
        self.widget = c
        self.rotDir = rotDir
        self.zeroAxis = zeroAxis
        self.setAngle(initAngle, doCallback=0)

        c.tag_bind(self.main, '<ButtonPress-1>', self.button_press_cb)
        c.tag_bind(self.main, '<Button1-Motion>', self.pointer_drag_cb)
        c.tag_bind(self.main, '<ButtonRelease-1>', self.button_release_cb)
        c.tag_bind(self.line_id, '<ButtonPress-1>', self.button_press_cb)
        c.tag_bind(self.line_id, '<Button1-Motion>', self.pointer_drag_cb)
        c.tag_bind(self.line_id, '<ButtonRelease-1>', self.button_release_cb)

        self.c = c

    def pack(self, *args, **kwargs):
        self.c.pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        self.c.grid(*args, **kwargs)

    def mid_press_cb(self, event):
        self.c.itemconfigure(self.mid, fill='red')
        self.press_command()

    def mid_release_cb(self, event):
        self.c.itemconfigure(self.mid, fill='white')
        self.release_command()

    def button_press_cb(self, event):
        try:
            self.drag_from_angle = self.event_angle(event)
        except ValueError:
            pass

    def pointer_drag_cb(self, event):
        if self.drag_from_angle == None:
            return

        try:
            a = self.event_angle(event)
        except ValueError:
            pass
        else:
            self.drag_from_angle = a
            self.set_angle(a)

    def button_release_cb(self, event):
        if self.drag_from_angle == None:
            return

        try:
            a = self.event_angle(event)
        except ValueError:
            pass
        else:
            delta = a - self.drag_from_angle
            self.drag_from_angle = None
            self.set_angle(a)

    # ---------------------------------------------------------------------------
    #
    def event_angle(self, event):
        # math.atan2 may raise ValueError if dx and dy are zero.
        (x, y) = canvas_coordinates(self.canvas, event)
        (dx, dy) = (x - self.center_xy[0], self.center_xy[1] - y)
        rad = math.atan2(dy, dx)
        deg = math.degrees(rad)
        if self.zeroAxis == 'y':
            deg = deg + 270
        elif self.zeroAxis == '-x':
            deg = deg + 180
        elif self.zeroAxis == '-y':
            deg = deg + 90

        if self.rotDir == 'clockwise':
            deg = 360 - deg

        while deg > 360.0:
            deg = deg - 360
        while deg <= 0:
            deg = deg + 360
        return deg

    # ---------------------------------------------------------------------------
    #
    def set_angle(self, a, doCallback=1):

        #
        # Move dial pointer
        #
        cx, cy = self.center_xy
        d = self.radius + self.bump_size
        cartesian = a
        if self.rotDir == 'clockwise':
            cartesian = 360 - cartesian
        if self.zeroAxis == 'y':
            cartesian = cartesian + 90
        elif self.zeroAxis == '-x':
            cartesian = cartesian + 180
        elif self.zeroAxis == '-y':
            cartesian = cartesian + 270
        while cartesian > 360.0:
            cartesian = cartesian - 360
        while cartesian <= 0.0:
            cartesian = cartesian + 360
        rad = math.pi * cartesian / 180.0
        ox = d * math.cos(rad)
        oy = d * math.sin(rad)
        ox2 = d/5 * math.cos(rad)
        oy2 = d/5 * math.sin(rad)
        self.canvas.coords(self.line_id, cx+ox2, cy-oy2, cx + ox, cy - oy)

        #
        # Call callback
        #
        if doCallback:
            self.command(a)

    setAngle = set_angle

# -----------------------------------------------------------------------------
#
def canvas_coordinates(canvas, event):

    return (canvas.canvasx(event.x), canvas.canvasy(event.y))