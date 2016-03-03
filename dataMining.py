""" Vittorio Beltracchi - 2015
    Purpose of this code is to read from two CSV
    files the training and test datasets.
    Then, on those calculate three distances:
    Euclidean, Manhattan and Cosine """

import math
from statistics import mode
import resource
import time

def euclidean(list_train, list_test):
    """Function to calculate the Euclidean distance"""

    distance = 0.0
    # Add up the squared differences, loop ignores the class in the record
    # stopping at len(list_train)-1
    for i in range(len(list_train)-1):
        distance += pow((float(list_test[i]) - float(list_train[i])),2)

    return math.sqrt(distance)


def manhattan(list_train, list_test):
    """Function to calculate the Manhattan distance"""

    distance = 0.0
    # Loop ignores the class in the record stopping at len(list_train)-1
    for i in range(len(list_train)-1):
        distance += abs(float(list_test[i]) - float(list_train[i]))

    return distance


def cosine(list_train, list_test):
    """Function to calculate the Cosine distance
       [1-sum(xi*yi)/sqroot(sum(xi)^2)*sqroot(sum(yi)^2)"""

    numerator = 0.0
    denom_1 = 0.0
    denom_2 = 0.0
    # Loop ignores the class in the record stopping at len(list_train)-1
    for i in range(len(list_train)-1):
    # For some reason (rounding or similar) if I don't split the equation
    # in different parts Python is giving me different results, hence here
    # the breakdown
        numerator += abs(float(list_test[i]) * float(list_train[i]))
        denom_1 += pow(float(list_train[i]),2)
        denom_2 += pow(float(list_test[i]),2)

    denom_1 = math.sqrt(denom_1)
    denom_2 = math.sqrt(denom_2)
    denom_3 = denom_1 * denom_2

    distance = 1 - (numerator / denom_3)

    return distance

def knn(mapped, test_class, k_val):
    """Function to calculate the knn, imput the sorted association distance/class
    the class of the test record and the value of k"""
    
    if k_val == 1:
        # If k is 1 just return the first value
        neighbor = (k_val,mapped[0][1],test_class)
    
    else:
        # Otherwise pick the first k value in the mapped list
        label_list = []
        
        for i in range(k_val):
            label_list.append(mapped[i][1])
            
        # calculate the mode on the k value picked
        train_class = mode(label_list)
        
        neighbor = (k_val,train_class,test_class)

    return neighbor
 
def process_file(tr_file, te_file):
    """Function to process the files, open, read and then call the knn"""

    # Open the files
    train_file = open(tr_file, "rU")
    test_file = open(te_file, "rU")

    # List to store the results
    eu_res = []
    ma_res =[]
    co_res = []
 
    # Declare k and its value
    k = [1, 3, 5, 9]

    # Remove the header from the files moving the pointer down one
    train_head = train_file.readline()
    test_head = test_file.readline()

    # Read the lines from the test file
    for entry in test_file:
        # Create or empty the mapping lists [(distance,train_class)]
        eu_map = []
        ma_map = []
        co_map = []
    
        # Process the line in the file, remove the NewLine and define the split
        entry_remove_nl = entry[:-1]
        test_record = entry_remove_nl.split(',')

        # Store the class of the test record
        test_label = int(test_record[-1])
        #print('Test record ' + str(test_record))

        # Read the lines from train file
        for tr_entry in train_file:
            # Same as before for the file process
            tr_entry_remove_nl = tr_entry[:-1]
            train_record = tr_entry_remove_nl.split(',')
            
            # Store the class of the train record
            train_label = int(train_record[-1])

            # Store distance between the test and the train node in a multi-dimensional list
            # Eucledian
            eu_dist = euclidean(train_record,test_record)
            eu_map.append((eu_dist,train_label))

            ma_dist = manhattan(train_record,test_record)
            ma_map.append((ma_dist,train_label))

            co_dist = cosine(train_record,test_record)
            co_map.append((co_dist, train_label))
            
 
        # Sort the values in ascending order (closer to further)
        eu_map.sort()
        ma_map.sort()
        co_map.sort()
        # Move back the pointer to the top of train file and remove the header again
        train_file.seek(0,0)
        train_head = train_file.readline()

        # Pass the map and k to knn and append its result
        for value in k:
            eu_res.append(knn(eu_map, test_label, value))
            ma_res.append(knn(ma_map, test_label, value))
            co_res.append(knn(co_map, test_label, value))
    train_file.close()
    test_file.close()

    # Compare the mode of the train class with the test class, are the same?
    # Print the table of results
    print("k | Euclidean correct/wrong") 
    for value in k:
        c_true = 0
        c_false = 0
        for item in eu_res:
            if item[0] == value and item[1] == item[2]:
                c_true += 1
            elif item[0] == value:
                c_false +=1

        print(str(value) + ' | ' + str(c_true) + '/' + str(c_false))
        
    print("\nk | Manhattan correct/wrong") 
    for value in k:
        c_true = 0
        c_false = 0
        for item in ma_res:
            if item[0] == value and item[1] == item[2]:
                c_true += 1
            elif item[0] == value:
                c_false +=1

        print(str(value) + ' | ' + str(c_true) + '/' + str(c_false))

    print("\nk | Cosine correct/wrong") 
    for value in k:
        c_true = 0
        c_false = 0
        for item in co_res:
            if item[0] == value and item[1] == item[2]:
                c_true += 1
            elif item[0] == value:
                c_false +=1

        print(str(value) + ' | ' + str(c_true) + '/' + str(c_false))

# MAIN
# Define the files to use
bc_train = 'breast-cancer-train.csv'
bc_test = 'breast-cancer-test-assignment.csv'
ir_train = 'iris-train.csv'
ir_test = 'iris-test-assignment.csv'

# Call the process_file on the defined files
print("Breast Cancer Dataset\n")
process_file(bc_train, bc_test)
print('\n---------------\n')
print("Iris Dataset\n")
process_file(ir_train, ir_test)

# Routine to retrieve the program statistics
# using standard resource library and its man suggested use
usage = resource.getrusage(resource.RUSAGE_SELF)
print('\n----- Module Statistics-----\n')
for name, desc in [
    ('ru_utime', 'User time'),
    ('ru_stime', 'System time'),
    ('ru_maxrss', 'Max. Resident Set Size'),
    ('ru_ixrss', 'Shared Memory Size'),
    ('ru_idrss', 'Unshared Memory Size'),
    ('ru_isrss', 'Stack Size'),
    ('ru_inblock', 'Block inputs'),
    ('ru_oublock', 'Block outputs'),
    ]:
    print('%-25s (%-10s) = %s' % (desc, name, getattr(usage, name)))
