
# Vittorio Beltracchi (C) 2014
# Obtain data from CSV files, analyse, and provide results

def process_data_file (filename):
    flag = False
    tot_list = []
    sum_temp = 0
    tot_hot_days = 0
    years_list = []

    while not flag:
        try:
            csvfile = open(filename, "rU")
            flag = True
        except IOError:
            print('\n--- ',filename,' FILE NOT FOUND!\n')
            filename = input('Enter a file name: ')

    header = csvfile.readline()

    for entry in csvfile:

        entry_without_newline = entry[:-1]

        # Discriminate values from noise
        if accept_entry(entry_without_newline):
            continue

        # Calculate the average and number of "very hot" days
        record = entry_without_newline.split(',')

        temp_tuple = (record[2],float(record[5]))

        tot_list.append(temp_tuple)

    csvfile.close()
    
    # Year average and number of 37+ days per each year
    year = tot_list[0][0]

    years_list.append(temp_tuple[0])

    year_temp_list = []
    year_hot_days = 0

    for temp_tuple in tot_list:
        # Control on the year field, if same year append to the year list
        if temp_tuple[0] == year:
            year_temp_list.append(temp_tuple[1])
        else:
            print()
            # Calculate the average and display it at the same time
            print('{:<5s}: average = {}'.format(year,sum(year_temp_list) / len(year_temp_list)))
            # Loop through the list looking for the 37+ days for that year
            for temperature in year_temp_list:
                if temperature > 37:
                    year_hot_days += 1
            print('{:<7s}number of 37+ days = {}'.format('',year_hot_days))
            # Reset all the value, ready for the following year
            year = temp_tuple[0]
            year_hot_days = 0
            year_temp_list[:] = []
            year_temp_list.append(temp_tuple[1])

            years_list.append(temp_tuple[0])

    # The latest print must be outside the loop if not is avoided
    print()
    print('{:<5s}: average = {}'.format(year,sum(year_temp_list) / len(year_temp_list)))
    for temperature in year_temp_list:
        if temperature > 37:
            year_hot_days += 1
    print('{:<7s}number of 37+ days = {}'.format('',year_hot_days))
    # Calculate total average over the file
    for temp_tuple in tot_list:
        sum_temp += temp_tuple[1]

        if temp_tuple[1] > 37 :
            tot_hot_days += 1

    print('\naverage =',sum_temp/ len(tot_list))
    print('number of 37+ days =',tot_hot_days)
    # Empty line to give some format
    print()

    # Split the time period in two not even halves, because of the quantity of data can be different.
    # Calculate the average per each half and display the results.
    # Having the valid data in a list comes handy at this point.
    # On the other hands, it is not recommended to store data locally, because we cannot be sure about their quantity.

    only_years_list = []
    only_temps_list = []

    for temp_touple in tot_list:
        only_years_list.append(temp_touple[0])
        only_temps_list.append(temp_touple[1])

    # Stored before a list of unique years, use the one in the half of it
    # as referiment for middle point, then I determine at which index
    # that year is found, the return value is the first index containing the year
    # in the middle of the whole number of years analysed
    mid_point = only_years_list.index(years_list[int(len(years_list)/2)])

    # Use this middle point to split the list in other two halves
    # used to calculate the average per sample
    first_sample = only_temps_list[:mid_point]
    first_years = only_years_list[:mid_point]
    second_sample = only_temps_list[mid_point:]
    second_years = only_years_list[mid_point:]

    first_avg = sum(first_sample)/len(first_sample)
    second_avg = sum(second_sample)/len(second_sample)
    # Then display
    print('average {:<4s}-{:<4s} = {}'.format(first_years[0], \
                                     first_years[-1], \
                                     first_avg))
    print('average {:<4s}-{:<4s} = {}'.format(second_years[0], \
                                     second_years[-1], \
                                     second_avg))
    # Empty all the used lists
    first_sample[:] = []
    first_years[:] = []
    second_sample[:] = []
    second_years[:] = []
    only_years_list[:] = []
    only_temps_list[:] = []
    year_temp_list[:] = []
    years_list[:] = []
    tot_list[:] = []

def accept_entry (entry):    
    # Must ignore noise
    line = entry.split(',')

    # Instruct all the conditions that must ignore the data
    # Field Year, Month, Day, Temperature or Quality is empty
    if line[2] =='' or line[3] =='' or line[4] =='' or line[5]=='' or line[7] =='' :
        # print('Found Blank')
        return True
    # The Quality field is 'N'
    elif line[7] == 'N' :
        # print('Found N')
        return True
    # The temperature value is out of the range of known realistic values
    elif float(line[5]) > 50.7 or float(line[5]) < -23 :
        #print('Found temp')
        return True
    else :       
        return False

if __name__ == "__main__":
    data_file_name = input("Enter file name: ")
    process_data_file(data_file_name)
