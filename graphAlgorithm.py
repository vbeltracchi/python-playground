# Vittorio Beltracchi (C) 2014
#
# Graph algorithms implementation: including DFS

def read_graph_from_file(filename):
    '''This function reads a graph from a file and returns a tuple of
    two lists: (neighbours, positions): neighbours is the neighbour
    list representation of the graph; positions is the list of node
    positions (this is used only for displaying the graph on screen).'''

    position_list = []
    node_link = []
    neighbour_list = []
    node = 0
    link_found = False

    csvfile = open(filename, 'rU')
    # Read the file, keep track of the line in the file at the same time,
    # used for the error handling

    for line, entry in enumerate(csvfile):

        entry_no_newline = entry[:-1]

        record = entry_no_newline.split(',')

        if len(record) == 3:
            # If the record has 3 elements is a node with position.
            # Hence store the coordinates in a sublist, and append it to the main position list

            # Handle nodes in file not ordered
            if int(record[0]) != node:
                raise FileFormatError(filename,line,'Nodes are not ordered!')

            # Handle not integer position coordinates
            elif isinstance(record[1],int) or isinstance(record[2],int):
                raise FileFormatError(filename,line,'Coordinates are not integer!')

            # Handle the mixed information in the file
            elif link_found:
                raise FileFormatError(filename,line,'Nodes and link are not in the correct sequence!')

            # All good
            else:
                tmp_pos = (int(record[1]),int(record[2]))
                position_list.append(tmp_pos)
                # Increase Node Counter/Value as reference
                node += 1

        if len(record) == 2:
            # Set the flag to True when I meet the first connection, from that down are all the same,
            # Check this flag above in case a node appears between the coordinates
            link_found = True

            # Manage the error of link to node out of range
            if int(record[0]) > len(position_list)-1 or int(record[1]) > len(position_list)-1:
                raise FileFormatError(filename,line,'Link Involves Nodes Out Of Range!')
            else:
                tmp_link = [int(record[0]),int(record[1])]
                tmp_link_rev = tmp_link[::-1]
                node_link.append(tmp_link)
                node_link.append(tmp_link_rev)
                node_link.sort()

    csvfile.close()

    # Use of the index of all the positions to refer to the exact node and manage
    # the connections with a nested loop.

    # Prints are for debugging purpose.
    # print(node_link)
    # print('-'*10)

    for index, item in enumerate(position_list):
        element_list = []
        for node in node_link:
            if node[0] == index:
                element_list.append(node[1])
        # print(index, element_list)

        neighbour_list.append(element_list)
    # print('-'*10)
    #print(position_list, len(position_list))
    #print(neighbour_list, len(neighbour_list))

    return (neighbour_list,position_list)

## Implementing this function is task 2:
def label_graph_components(neighbour_list):
    '''This function takes as input the neighbour list representation of
    a graph and returns a list with the component number for each node in
    the graph. Components must be numbered consecutively, starting from
    zero.'''

    # Labelled list initialised at -1
    label_list = [-1]*len(neighbour_list)

    # Define a set for visited nodes
    visited = set()
    # Define first label that is 0
    label = 0

    # Walk the graph with Depth-First Search
    # The label is passed as parameter and managed to maintain the consecutive increment of the label itself.
    # For this reason, chose to return the label value from/to the recursive call.

    def node_labelling(n,l):
        # Ignore visited nodes
        if n in visited:
            # return the label itself and do nothing else
            return l
        else:
            # Add the node to the visited
            visited.add(n)
            # Check if already labelled, and label it
            if label_list[n] == -1:
                label_list[n] = l

            # Recursive call on the neighbour nodes
            for neighbour in neighbour_list[n]: 
                node_labelling(neighbour,l)
            # Increment label for a new graph component, return it
            l += 1
            return l

    # Main call of the function, passing the grph and the label
    for node,item in enumerate(neighbour_list):
        label = node_labelling(node,label)

    # print("visited:",visited)
    # print("label list:",label_list)

    return label_list

def get_component_density(label, neighbour_list, label_list):
    '''This function takes a component label, the neighbour list
    representation of a graph and a list of component labels
    (one for each node in the graph), and should calculate and return
    the link density in the component with the given label. The link
    density is defined as the number of links (in that component)
    divided by the number of nodes (in that component). If there
    are no nodes with the given component label, the function
    should raise an error.'''

    # Handle the node without a label
    if label == None:
        raise FileFormatError("ERROR",000,"Found node without a label!")

    # Count how many nodes in the component
    node_count = 0

    for element in label_list:
        if element == label:
            node_count += 1
    #print("Label ",label," has ",node_count," nodes")

    # Count how many link in the component
    # Define a set to avoid repetitions, not really necessary but careful
    link_count = set()
    # Loop through the label list to identify the same component nodes
    # If the label is the same as the parameter enter in another loop
    # where the neighbour_list is analysed, then add the values to the set
    for node,lbl in enumerate(label_list):
        if lbl == label:
            for link in neighbour_list[node]:
                if (link,node) not in link_count:
                    link_count.add((node,link))
    #print("Label",label,"has",len(link_count),"links")

    # Here density of a component is the number of its links divided by
    # the number of its nodes, then return the value
    density = len(link_count) / node_count

    return density

# Component is a Tree analysis
def component_is_a_tree(label, neighbour_list, label_list):
    '''This function takes a component label, the neighbour list
    representation of a graph and a list of component labels
    (one for each node in the graph), and should evaluate if the component
    is a tree. Otherwise, if the component does not contain cycles. It returns
    True in this case. Based on the theorem that in an UNDIRECTED graph the maximum
    number of edges is equal to the number of vertex minus one (E = V-1).'''

    # Simple Theorem, valid with limitation to UNDIRECTED graphs:
    # For UNDIRECTED graph/component, we have a tree, there are no cycles,
    # if the maximum number of edges/link E and is equal to the number of
    # vertex(nodes) minus one. E = V - 1

    # Reuse of the DFS algorithm instructed in the get_component_density function
    # To analyse the graph component, in terms of number of nodes and links
    node_count = 0

    for element in label_list:
        if element == label:
            node_count += 1

    link_count = set()

    for node,lbl in enumerate(label_list):
        if lbl == label:
            for link in neighbour_list[node]:
                if (link,node) not in link_count:
                    link_count.add((node,link))
    #print(len(link_count),node_count)

    # Apply the theorem max number of E = number of V-1
    if len(link_count) <= node_count - 1:
        return True
    else:
        return False

class FileFormatError (Exception):
    def __init__(self, filename, line_num, message):
        super(Exception, self).__init__()
        self.filename = filename
        self.line_num = line_num
        self.message = message
    def __str__(self):
        return self.filename + ", line " + str(self.line_num) + ": " + self.message
