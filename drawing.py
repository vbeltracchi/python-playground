
## To run in python2, change tkinter to Tkinter.
import tkinter as tk
import math

def show_graph(neighbour_list, position_list,
               title_str="Graph", label_list=None, node_radius=18, margin=5):
    '''This function shows the given graph in a pop-up window.
    neighbour_list is the internal representation of the graph
    structure (list of lists of neighbours);
    position_list is a list of tuples (x,y), the i:th tuple in the
    list giving the position of node i;
    the two lists must be of the same length, which must also be equal
    to the number of nodes.
    The function has four optional (keyword) parameters:
    title_str is the title to use on the pop-up window.
    label_list is a list of component labels, or None.
    If label_list != None, it must also be the same length as the other
    two lists, and the component labels must be integers ranging from 0
    to the number of components (which should never be greater than the
    number of nodes). If label_list is given, the function will colour
    nodes to show which component they belong to.
    node_radius specifies how large nodes should be drawn; note that
    changing it will not change the size of the text showing the node
    number.
    margin is the margin (in pixels) between the outer edges of the
    outermost nodes and the edge of the drawing area. It is the same
    on all four sides.'''
    number_of_nodes = len(neighbour_list)
    assert len(position_list) == number_of_nodes, \
        "length of link and position lists differ"
    number_of_labels = 1
    if label_list != None:
        assert len(label_list) == number_of_nodes, \
            "length of label_list differs from link/position lists"
        for label in label_list:
            assert isinstance(label, int), "invalid label: " + str(label)
            assert 0 <= label, "negative label: " + str(label)
            number_of_labels = max(number_of_labels, label + 1)
    (xoff, xmax, yoff, ymax) = \
        graph_drawing_offset_and_size(position_list, node_radius, margin)
    root = tk.Tk()
    try:
        root.wm_title(title_str)
        frame = tk.Frame(root)
        frame.pack()
        canvas = tk.Canvas(frame, width=xmax, height=ymax, bg="white")
        for i in range(number_of_nodes):
            for j in neighbour_list[i]:
                if j > i:
                    (xi,yi) = position_list[i]
                    (xj,yj) = position_list[j]
                    canvas.create_line(xi + xoff, yi + yoff,
                                       xj + xoff, yj + yoff,
                                       width=1, fill="black")
        if label_list != None:
            colors = [ rgb_to_hex(r,g,b)
                       for (r,g,b) in make_rainbow(number_of_labels) ]
        for i in range(number_of_nodes):
            (xi,yi) = position_list[i]
            if label_list != None:
                canvas.create_oval(xi + xoff - node_radius,
                                   yi + yoff - node_radius,
                                   xi + xoff + node_radius,
                                   yi + yoff + node_radius,
                                   outline="black", fill=colors[label_list[i]])
            else:
                canvas.create_oval(xi + xoff - node_radius,
                                   yi + yoff - node_radius,
                                   xi + xoff + node_radius,
                                   yi + yoff + node_radius,
                                   outline="black", fill="white")
            canvas.create_text(xi + xoff, yi + yoff, text=str(i), fill="black")
        canvas.pack(side="top")
        close_button = tk.Button(frame, text="Close", command=root.destroy)
        close_button.pack(side="bottom")
        ## To run in python2 on windows, the following line must be uncommented.
        ## In python3, on GNU/linux, however, this causes IDLE to freeze.
        #root.mainloop()
    except Exception as exc:
        root.destroy()
        raise exc

def graph_drawing_offset_and_size(position_list, node_radius, margin):
    '''This function calculates an offset and size of the drawing area
    based on input node positions, node radius and margin (space between
    the edge of the outermost nodes and the border of the drawing area).
    Returns a tuple of four values: (xoff, xmax, yoff, ymax). The drawing
    function should add xoff, yoff to the x, y positions of each node.'''
    xs = [ x for (x,y) in position_list ]
    ys = [ y for (x,y) in position_list ]
    xoff = node_radius + margin - min(xs)
    xmax = max(xs) + xoff + node_radius + margin
    yoff = node_radius + margin - min(ys)
    ymax = max(ys) + yoff + node_radius + margin
    return (xoff, xmax, yoff, ymax)

def make_rainbow(n):
    '''This function returns a list of floating point RGB color specs,
    forming a "rainbow" with n elements. (It is used by drawing functions
    to colour n elements with "different colours" in a systematic way.)'''
    step = 360.0 / n
    return [ hsl_to_rgb(i * step, 1, 0.5) for i in range(n) ]

def hsl_to_rgb(hue, saturation, lightness):
    '''Convert HSL color to RGB (http://en.wikipedia.org/wiki/HSL_and_HSV).
    Constraints on input: hue (int) in [0, 360), saturation (float) in [0,1],
    lightness (float) in [0,1].'''
    assert(0 <= hue < 360)
    assert(0 <= saturation <= 1)
    assert(0 <= lightness <= 1)
    hp = hue / 60.
    c = (1 - math.fabs((2 * lightness) - 1)) * saturation
    x = c * (1 - math.fabs((hp % 2) - 1))
    if hp < 1:
        (r1, g1, b1) = (c,x,0)
    elif hp < 2:
        (r1, g1, b1) = (x,c,0)
    elif hp < 3:
        (r1, g1, b1) = (0,c,x)
    elif hp < 4:
        (r1, g1, b1) = (0,x,c)
    elif hp < 5:
        (r1, g1, b1) = (x,0,c)
    else:
        (r1, g1, b1) = (c,0,x)
    m = lightness - c/2
    return (r1 + m, g1 + m, b1 + m)

def rgb_to_hex(red, green, blue):
    '''Convert a floating point RGB color spec to a hex string that can
    be used with drawing functions. Arguments must all be floats in [0,1]'''
    assert(0 <= red <= 1)
    assert(0 <= green <= 1)
    assert(0 <= blue <= 1)
    red_int = int(255 * red)
    green_int = int(255 * green)
    blue_int = int(255 * blue)
    return "#{:02x}{:02x}{:02x}".format(red_int, green_int, blue_int)
