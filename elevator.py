# ===================================
# Vittorio Beltracchi (C) 2014
# Elevator events simulator
# ===================================

from simulator import *

## Task 1 (2 marks):

class UpTrafficGenerator (UniformTrafficGenerator):
    '''A TrafficGenerator that creates only passengers going UP from
    the ground floor; that is, passengers all have origin = 0, and
    destination chosen (uniformly) at random from the other floors.
    This class is made a subclass of the UniformTrafficGenerator
    because it simplifies implementation.'''

    ## Constructor. You may NOT change the arguments to the constructor.
    def __init__(self, floors, mean_time, simulator):
        # The constructor MUST call the superclass constructor.
        UniformTrafficGenerator.__init__(self, floors, mean_time, simulator)
        # You can add further initialisation code to the constructor
        # if you wish.

    ## You should implement other methods of the class here.
    def choose_origin_and_destination(self):
        '''Internal helper method to select random origin and destination
        floors. Should return a tuple of two integers, which MUST NOT be
        equal.'''
        orig = 0
        dest = int(self.random.randint(1, len(self.floors)-1))
        return (orig, dest)

# end class UpTrafficGenerator

class DownTrafficGenerator (UniformTrafficGenerator):
    '''A TrafficGenerator that creates only passengers going DOWN to
    the ground floor; that is, passengers all have destination = 0,
    and origin chosen (uniformly) at random from the other floors.
    This class is made a subclass of the UniformTrafficGenerator
    because it simplifies implementation.'''

    ## Constructor. You may NOT change the arguments to the constructor.
    def __init__(self, floors, mean_time, simulator):
        # The constructor MUST call the superclass constructor.
        UniformTrafficGenerator.__init__(self, floors, mean_time, simulator)
        # You can add further initialisation code to the constructor
        # if you wish.

    ## You should implement other methods of the class here.
    def choose_origin_and_destination(self):
        '''Internal helper method to select random origin and destination
        floors. Should return a tuple of two integers, which MUST NOT be
        equal.'''
        orig = int(self.random.randint(1, len(self.floors)-1))
        dest = 0
        return (orig, dest)
    
# end class DownTrafficGenerator

## Task 2(a) (2 marks) and 2(b) (2 marks):

class FloorStatistics (Floor):
    '''A FloorStatistics object monitors all floors and collects some
    key statistics that are not available from the other statistics
    objects. In particular, for each floor, it should record:
    (a) the maximum number of passengers waiting on that floor at any
        time; and
    (b) the average number of passengers boarding each time an elevator
        stops at that floor.
    The constructor argument, floors, is the list of Floor objects,
    ordered by level from 0 (ground floor) to number of floors - 1.
    The print_summary method is called after the simulator run is
    finished.'''
    def __init__(self, floors):
        '''Declare and initialise needed variables and data structures'''
        self.floors = floors
        ## Add code to perform necessary initialisation here.
        for floor in floors:
            floor.add_watcher(self)
        
        # List to contain the number of passenger waiting, index is floor
        self.list_waiting = [0]*len(self.floors)

        # Counters to keep track of the passenger waiting each time on the floor,
        # to be compared with the previous amount
        self.count_waiting = 0

        # Number of passenger previously measured on each floor
        self.count_previous = [0]*len(self.floors)

        # Counter to keep track of how many time we notify this watcher, and
        # counter to keep track of the boarding passengers
        self.count_calls = [0]*len(self.floors)
        self.count_boarding = [0]*len(self.floors)
        
    ## You should implement other methods that the class needs here.
        
    def update(self,obj):
        '''Callback method for when a watched floor notifies of a state
        change.'''
        # Assumed that the object is a Floor type
        assert isinstance(obj,Floor)

        # Sum app the number of passenger presently waiting on the floor            
        self.count_waiting = len(obj.waiting_to_go_up) + len(obj.waiting_to_go_down)

        # TASK (a) Maximum number of passenger waiting on the floors
        # If this amount is bigger than the one previously recorded overwrite
        if self.count_waiting > self.list_waiting[obj.level]:
            self.list_waiting[obj.level] = self.count_waiting

        # TASK (b)Average of passengers boarding on the floors
        # If the number of people waiting decreased
        if self.count_waiting < self.count_previous[obj.level]:
            # A boarding happened
            self.count_calls[obj.level] += 1
            # Store this value in the list, at the index corresponding to the floor
            self.count_boarding[obj.level] += self.count_previous[obj.level] - self.count_waiting
            # The average is calculated directly in the print_summary.
        # The previous measure change at this point, ready for next iteration
        self.count_previous[obj.level] = self.count_waiting
               
    def print_summary(self):
        for floor in self.floors:
            ## You MUST REPLACE the 0 and 0.0 in the following print call
            ## with the values you have calculated!
            
            # Assumed that the value of number of calls is greater than 0
            # to avoid ZeroDivisionError
            assert  self.count_calls[floor.level] > 0
            print("Level {:3d}: max {:d} waiting, average {:.3f} boarding".format(floor.level, self.list_waiting[floor.level],self.count_boarding[floor.level] / self.count_calls[floor.level]))
            
# end class FloorStatistics

## Task 3 (2 marks):

class TimeVaryingGenerator(SimulatorObject):
    '''A TimeVaryingGenerator object takes a traffic generator object
    and a schedule of (time, value) tuples, and updates the mean arrival
    time of the generator object at each time in the schedule to the
    given value. Schedule times are given seconds after midnight, and
    should be applied to each day if the simulation runs over several
    days. For example, if the schedule is [(32400, 10), (61200, 300)],
    the mean time parameter should be set to 10 at 9am and to 300 at
    5pm, for every simulated day.
    The simulator argument is the simulator object.
    You may make TimeVaryingGenerator a subclass of an existing class
    if you find this helpful.'''

    # Number of seconds in a day:
    DAY_SECONDS = 24 * 3600

    def __init__(self, generator, schedule, simulator):
        self.generator = generator
        self.schedule = schedule
        ## Add code to perform necessary initialisation here.
        SimulatorObject.__init__(self, simulator)

        # Variable to store the extaact next schedule time
        self.nx_schedule_time = 0
        # Variable to store the current schedule value
        self.cur_schedule_value = 0
        
    ## To help you with this task, two utility methods to extract
    ## information from the schedule are provided.

    def next_schedule_time(self, current_time):
        '''Returns the time of the next switch in the schedule, given
        the current simulated time.'''
        # Calculate the current day (since start of simulation), and
        # the current time (seconds since midnight) of that day.
        current_day = current_time // TimeVaryingGenerator.DAY_SECONDS
        current_time_of_day = current_time % TimeVaryingGenerator.DAY_SECONDS
        i = 0
        while i < len(self.schedule):
            if self.schedule[i][0] > current_time_of_day:
                return (current_day * TimeVaryingGenerator.DAY_SECONDS) + self.schedule[i][0]
            i += 1
        # If there is no more event in the schedule, the next event is the
        # first event on the next day:
        assert len(self.schedule) > 0
        return ((current_day + 1) * TimeVaryingGenerator.DAY_SECONDS) + self.schedule[0][0]

    def current_schedule_value(self, current_time):
        '''Returns the parameter value that should apply at the current
        time, according to the schedule.'''
        current_time_of_day = current_time % TimeVaryingGenerator.DAY_SECONDS
        assert len(self.schedule) > 0
        # If current time is before the first switch, the current value
        # is the value from the last switch on the previous day:
        if self.schedule[0][0] > current_time_of_day:
            return self.schedule[len(self.schedule) - 1][1]
        i = 1
        while i < len(self.schedule):
            if self.schedule[i][0] > current_time_of_day:
                return self.schedule[i - 1][1]
            i += 1
        return self.schedule[len(self.schedule) - 1][1]

    ## Add other methods that the class needs here.
    
    def start_run(self,start_time):
        '''Callback at the beginning'''
        # Get the value of next scheduled time
        self.nx_schedule_time = self.next_schedule_time(start_time)
        # Get the value of current scheduled value
        self.cur_schedule_value = self.current_schedule_value(start_time)
        #print('Next scheduled time',self.nx_schedule_time)
        #print('Current scheduled value',self.cur_schedule_value)
        
        # Delta
        dt = self.nx_schedule_time - start_time
        #print('Delta',dt)

        # Schedule next event
        self.schedule_next_event(dt,self.update)

    def update(self):
        '''Callback to update the mean and callback the start_run'''
        # Set the new mean with the value extracted
        self.generator.set_mean_time(self.cur_schedule_value)
        # Callback the start_run function
        self.start_run(self.nx_schedule_time)
        
        
# end class TimeVaryingGenerator

# ========================================================================
# TASK COMP6730 (3 marks)
# ========================================================================
class BalancedDispatcher(Dispatcher):
    '''Balanced Dispatcher that dispatch passenger to a random idle elevator,
    if any available.'''

    def __init__(self, elevators, floors, simulator):
        Dispatcher.__init__(self, elevators, floors, simulator)

    def call(self,level,direction):
        '''Overriden the call function. Here it manages the idle elevators randomly'''
        # List of idle elevators, and random generated number
        self.list_idle_elevator = []
        self.random = Random()

        # Store the idle elevator in a list
        for elevator in self.elevators:
            if elevator.state == Elevator.IDLE:
                self.list_idle_elevator.append(elevator)

        # If the lenght of the list is 0, there are no idle elevators,
        # Call is queued
        if len(self.list_idle_elevator) == 0:
           self.waiting_calls.append((level,direction))
        # If there is only 1 idle elevator, that is the one to dispatch
        elif len(self.list_idle_elevator) == 1:
            self.list_idle_elevator[0].dispatch(level,direction)
        # Otherwise randomise between the available elavator and dispatch there
        else:
            self.list_idle_elevator[self.random.randint(0,len(self.list_idle_elevator)-1)].dispatch(level,direction)        
# ========================================================================
# End of TASK COMP6730
# ========================================================================


## To test tasks 1 .. 3, set the following variables to True.
## You can test each task individually, or all of them together.

TEST_TASK_1 = True
TEST_TASK_2 = True
TEST_TASK_3 = True
TEST_EXTRA_6730 = True

# Change to True for lots of printing during simulation run.
VERBOSE = False

## Do NOT modify the main procedure!
if __name__ == '__main__':

    # Create a simulator:
    simulator = Simulator()

    # Construct a building with 70 floors and N identical elevators.
    number_of_elevators = 3
    elevator_capacity = 10 # number of passengers
    elevator_max_speed = 4.5 # in floors/second
    elevator_acceleration = 1.5 # in floors/second^2

    floors = [ Floor(i) for i in range(70) ]
    elevators = [ Elevator(i + 1, elevator_capacity, elevator_max_speed,
                           elevator_acceleration, 0, floors, simulator)
                  for i in range(number_of_elevators) ]

    # Create a dispatcher for the building.
    if TEST_EXTRA_6730:
        dispatcher = BalancedDispatcher(elevators, floors, simulator)
    else:
        dispatcher = Dispatcher(elevators, floors, simulator)

    # The stats objects collect statistics about elevators and passengers.
    estats = ElevatorStatistics(simulator)
    for elevator in elevators:
        elevator.add_watcher(estats)
    pstats = PassengerStatistics(simulator)
    Passenger.logs = [pstats]

    # For verbose output, create an event printer object, and set
    # it to monitor elevators and passengers.
    if VERBOSE:
        printer = PrintEvents(simulator)
        for elevator in elevators:
            elevator.add_watcher(printer)
        Passenger.logs.append(printer)

    if TEST_TASK_1:
        # To test task 1, create one traffic generator for each direction.
        up_tg = UpTrafficGenerator(floors, 13, simulator)
        dn_tg = DownTrafficGenerator(floors, 13, simulator)
    else:
        # Create a random traffic generator:
        rtg = UniformTrafficGenerator(floors, 6.5, simulator)

    if TEST_TASK_2:
        # To test task 2: create a FloorStatistics object, add it as a
        # watcher of all floors, and add a call to print_summary at end.
        fstats = FloorStatistics(floors)

    if TEST_TASK_3:
        # To test task 3, wrap the traffic generator(s) in time-varying
        # parameter schedules.
        if TEST_TASK_1:
            up_sched = [(0 * 3600, 60), (8 * 3600, 10), (9 * 3600, 5),
                        (10 * 3600, 15), (13 * 3600, 5), (14 * 3600, 15),
                        (17 * 3600, 30), (18 * 3600, 60)]
            up_tg = TimeVaryingGenerator(up_tg, up_sched, simulator)
            dn_sched = [(0 * 3600, 60), (9 * 3600, 15), (12 * 3600, 5),
                        (13 * 3600, 15), (16 * 3600, 10), (17 * 3600, 5),
                        (18 * 3600, 60)]
            dn_tg = TimeVaryingGenerator(dn_tg, dn_sched, simulator)
        else:
            sched = [(0 * 3600, 60), (7 * 3600, 15), (9 * 3600, 10),
                     (11 * 3600, 5), (13 * 3600, 10), (15 * 3600, 15),
                     (18 * 3600, 60)]
            rtg = TimeVaryingGenerator(rtg, sched, simulator)
            
    # Run the simulator for 36 hours, starting at 7am:
    simulator.run(7 * 3600, (7 + 12) * 3600)
    # ...and print stats at the end of the run:
    pstats.print_summary()
    estats.print_summary()
    if TEST_TASK_2:
        fstats.print_summary()
