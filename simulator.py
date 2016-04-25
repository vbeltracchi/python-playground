
import math
from heapq import *
from random import Random

class Observable (object):
    '''Base class for (simulated) objects that have an observable state.
    Other objects can register as "watchers" of an observable object. When
    the observable object changes state, it notifies all watchers. (This
    is not automatic, the object must call self.notify(). See for example
    the set_time method of the GlobalClock class below.)'''
    def __init__(self):
        self.watchers = set()

    def add_watcher(self, obj):
        self.watchers.add(obj)

    def remove_watcher(self, obj):
        try:
            self.watchers.remove(obj)
        except KeyError:
            pass

    def notify(self):
        '''Notify watchers that this object has been updated. Watchers
        must implement a method update(self, watched_object).'''
        for obj in self.watchers:
            obj.update(self)

# end class Observable


class GlobalClock (Observable):
    '''A class that keeps track of simulated time. The clock is observable
    (will notify watchers when time changes), but does not itself update
    time. (This is done by the Simulator class below.)'''
    def __init__(self):
        Observable.__init__(self)
        self.time = 0

    def get_time(self):
        '''Returns the current simulated time.'''
        return self.time

    def set_time(self, new_time):
        '''Set the current simulated time. This method should ONLY be
        called from the Simulator.'''
        self.time = new_time
        self.notify()

# end class GlobalClock
        

class Simulator (GlobalClock):
    '''The main simulator class.
    When the simulation runs, the simulator keeps a queue of future events.
    An event is a tuple (time, obj, method). When simulated time reaches
    the specified event time, the simulator will call the method on the
    object. Each object can only have one scheduled next event. The
    simulator uses the 'heapq' module to keep the queue ordered by event
    time. The simulator also keeps a list of objects that will be notified
    when simulation starts and ends.'''
    def __init__(self):
        GlobalClock.__init__(self)
        self.objects = []
        self.queue = []

    def register(self, obj):
        '''Add an object to the simulator. The object will be notified
        when simulation begins and ends, by calling start_run(self, time)
        and end_run(self, time), respectively.'''
        self.objects.append(obj)

    def schedule_next_event(self, obj, call, delta):
        '''Schedule a callback for object 'obj' at time now + delta. An
        object can only have one scheduled callback; if there is already
        a future event associated with the object, it will be replaced.'''
        for (pos, (_, queue_obj, _)) in enumerate(self.queue):
            if queue_obj == obj:
                self.queue[pos] = (self.get_time() + delta, obj, call)
                heapify(self.queue)
                return
        heappush(self.queue, (self.get_time() + delta, obj, call))

    def run(self, start_time, end_time):
        '''Run a simulation from start_time to end_time.'''
        self.set_time(start_time)
        self.queue = []
        for obj in self.objects:
            obj.start_run(start_time)
        heapify(self.queue)

        next_time = end_time
        if len(self.queue) > 0:
            (next_time, obj, method) = self.queue[0]
            try:
                heappop(self.queue)
            except TypeError:
                print("type error in heappop")
                for (index, entry) in enumerate(self.queue):
                    print(index, ":", entry)
        while next_time < end_time:
            if next_time > self.get_time():
                self.set_time(next_time)
            method()
            next_time = end_time
            if len(self.queue) > 0:
                (next_time, obj, method) = self.queue[0]
                try:
                    heappop(self.queue)
                except TypeError:
                    print("type error in heappop")
                    for (index, entry) in enumerate(self.queue):
                        print(index, ":", entry)

        self.set_time(end_time)
        for obj in self.objects:
            obj.end_run(end_time)

# end class Simulator


class SimulatorObject (object):
    '''SimulatorObject is a base class for "active" objects that will
    request callbacks from the simulator. It keeps track of the simulator
    object, provides default (do-nothing) implementations of start_run
    and end_run, and a short-cut to scheduling events.'''
    def __init__(self, simulator):
        self.simulator = simulator
        simulator.register(self)

    def __lt__(self, other):
        return id(self) < id(other)

    # All simulator objects must implement the start_run and end_run
    # methods. The defaults are do-nothing implementation for objects
    # that don't need to do anything at the beginning or end.
    def start_run(self, start_time):
        pass

    def end_run(self, end_time):
        pass

    def schedule_next_event(self, delta, call):
        self.simulator.schedule_next_event(self, call, delta)

# end class SimulatorObject

# Here, we define three symbolic names (constants) used to indicate
# directions. (The "constants" are actually variables, but we keep
# them constant by NEVER assigning new values to them.)

DIR_UP = 1
DIR_NONE = 0
DIR_DOWN = -1


class Elevator (SimulatorObject, Observable):
    '''Simulator object for an elevator. The implementation of the
    elevator control strategy is split between this object and the
    Dispatcher object defined below. The arguments to the Elevator
    constructor are:
    name - an identifier for the elevator (typically, 1,2,3,...).
    capacity (int) - max number of people in the elevator.
    v_max (float) - max elevator speed, in floors/second.
    acc (float) - elevator acceleration, in floors/second.
    start_level (int) - where the elevator is at simulation start.
    floor_list - list of Floor objects (ordered by level, 0 .. #floors-1)
    simulator - the simulator object.'''

    # Constants used in the Elevator logic.
    IDLE = 0
    DOORS_OPEN = 1
    MOVING = 2

    def __init__(self, name, capacity, v_max, acc, start_level, floor_list, simulator):
        SimulatorObject.__init__(self, simulator)
        Observable.__init__(self)
        self.name = name
        self.capacity = capacity
        self.v_max = v_max
        self.acc = acc
        self.starting_level = start_level
        #self.next_stop = (None, DIR_NONE)
        #self.passengers = {}
        self.floors = floor_list

    def set_dispatcher(self, dispatcher):
        '''Called by the dispatcher to inform the elevator that it is
        now controlled by this dispatcher.'''
        self.dispatcher = dispatcher

    def start_run(self, start_time):
        '''Callback for the start of a simulator run. Initialise elevator
        state and notify observers.'''
        self.state = Elevator.IDLE
        self.current_level = self.starting_level
        self.next_stop = (None, DIR_NONE)
        self.passengers = {}
        self.notify()

    def get_load(self):
        '''Returns the number of passengers currently in the elevator.'''
        total = 0
        for (level, plist) in self.passengers.items():
            total += len(plist)
        return total

    def get_free(self):
        '''Returns the current free capacity in the elevator, i.e.,
        number of people that can board it.'''
        return self.capacity - self.get_load()

    def calculate_travel_time(self, level1, level2):
        '''Computes the travel time, in seconds, between stopped at
        level1 and stopped at level2.'''
        distance = level1 - level2
        if distance < 0:
            distance = -distance
        threshold = (self.v_max ** 2) / 2*self.acc
        if distance > threshold:
            cruise = distance - threshold
            t = 2 * (self.v_max / self.acc) + (cruise / self.v_max)
        else:
            t = math.sqrt(2 * distance / self.acc)
        return t

    def move_to(self, floor, direction):
        '''Internal helper method: set elevator state to moving (to
        the target floor) and schedule an event when it arrives.'''
        self.state = Elevator.MOVING
        tt = self.calculate_travel_time(floor.level, self.current_level)
        self.next_stop = (floor, direction)
        self.schedule_next_event(tt, self.arrive)

    def dispatch(self, level, direction):
        '''This method is called by the Dispatcher when a call for
        an elevator (to floor 'level', going in 'direction') is made,
        and the elevator is idle.'''
        assert 0 <= level < len(self.floors)
        assert self.state == Elevator.IDLE
        self.move_to(self.floors[level], direction)
        # State has been updated, so notify elevator's watchers
        self.notify()

    def arrive(self):
        '''Callback method for when the elevator arrives at its next
        stop. (The next stop, floor and direction, is stored in 
        self.next_stop. Note that the 'direction' part of next_stop is
        the direction that the elevator will continue in after the stop;
        it may be DIR_NONE.)'''
        (floor, direction) = self.next_stop
        self.current_level = floor.level
        self.state = Elevator.DOORS_OPEN
        # Find the number of passengers getting off at this stop; this
        # is obtained from the data stored in self.passengers.
        number_exiting = 0
        if self.current_level in self.passengers:
            number_exiting = len(self.passengers[self.current_level])
            for passenger in self.passengers[self.current_level]:
                passenger.exit()
            del self.passengers[self.current_level]
        # Ask the floor object how many passengers will enter the
        # elevator at this stop.
        entering = floor.get_passengers_entering(direction, self.get_free())
        number_entering = len(entering)
        for passenger in entering:
            if passenger.destination in self.passengers:
                self.passengers[passenger.destination].append(passenger)
            else:
                self.passengers[passenger.destination] = [passenger]
            # The passenger object is passive; we have to tell it that
            # it has boarded an elevator.
            passenger.board()
        # State has been updated, so notify elevator's watchers.
        self.notify()
        # Calculate the time it will take passengers to exit/board the
        # elevator (guesstimated at 2 seconds/passenger exiting and
        # 3 seconds/passenger boarding) and schedule an event when it
        # is done.
        dt = (number_exiting * 2) + (number_entering * 3)
        self.schedule_next_event(dt, self.doors_close)


    def doors_close(self):
        '''Callback method for when the elevator has finished unloading
        and boarding passengers at its current stop. This method figures
        out what the next stop (if any) will be, and updates the elevator
        state.'''
        (next_level, next_dir) = (None, DIR_NONE)
        # Find destinations of passengers in the elevator:
        dests = self.passengers.keys()
        if len(dests) > 0:
            # If all passengers are going up...
            if min(dests) > self.current_level:
                self.choose_next_stop_up(dests)
            # else, if all passengers are going down...
            elif max(dests) < self.current_level:
                self.choose_next_stop_down(dests)
            # else, passengers want to go both up and down!
            else:
                (this_stop_level, this_stop_dir) = self.next_stop
                # If we arrived at this floor with the intention of
                # going up, we prioritise that direction:
                if this_stop_dir == DIR_UP:
                    dests_up = [ level for level in dests if level > self.current_level ]
                    self.choose_next_stop_up(dests_up)
                # else, we arrived intending to go down, or we have no
                # planned direction, in which case we select a downwards
                # next stop:
                else:
                    dests_down = [ level for level in dests if level < self.current_level ]
                    self.choose_next_stop_down(dests_down)
                
        # If there are no passengers in the elevator, we ask the dispatcher
        # for a next (pick-up) stop.
        else:
            (next_level, next_dir) = self.dispatcher.get_pickup(self.current_level)

            # If the dispatcher gave us a destination, move:
            if next_level != None:
                self.move_to(self.floors[next_level], next_dir)
            # else, the elevator is now idle.
            else:
                self.state = Elevator.IDLE
        # Whichever case above occurred, state may have updated so we must
        # notify watchers.
        self.notify()

    def choose_next_stop_up(self, destinations):
        '''Internal helper method to select the next stop among a
        non-empty list of destinations. All destinations should be
        ABOVE the current level.'''
        assert len(destinations) > 0
        # The obvious next stop is the first (nearest) destination.
        next_level = min(destinations)
        # If there are passengers going beyond next stop, the
        # next direction will be up, otherwise it is undecided:
        if len(destinations) > 1:
            next_dir = DIR_UP
        else:
            next_dir = DIR_NONE
        # If we have capacity to spare, ask the dispatcher if we
        # should stop to pick up more passengers before the next
        # drop-off:
        if self.get_free() > 0:
            (next_level, next_dir) = self.dispatcher.get_pickup(self.current_level, next_level, next_dir)
        # Now get the elevator moving!
        self.move_to(self.floors[next_level], next_dir)
        self.notify()

    def choose_next_stop_down(self, destinations):
        '''Internal helper method to select the next stop among a
        non-empty list of destinations. All destinations should be
        BELOW the current level.'''
        assert len(destinations) > 0
        # The obvious next stop is the first (nearest) destination.
        next_level = max(destinations)
        # If there are passengers going beyond next stop, the
        # next direction will be up, otherwise it is undecided:
        if len(destinations) > 1:
            next_dir = DIR_DOWN
        else:
            next_dir = DIR_NONE
        # If we have capacity to spare, ask the dispatcher if we
        # should stop to pick up more passengers before the next
        # drop-off:
        if self.get_free() > 0:
            (next_level, next_dir) = self.dispatcher.get_pickup(self.current_level, next_level, next_dir)
        # Now get the elevator moving!
        self.move_to(self.floors[next_level], next_dir)
        self.notify()


    def __str__(self):
        '''Return a string describing the current state of the elevator.'''
        if self.state == Elevator.IDLE:
            return "Elevator " + str(self.name) + " IDLE at " + str(self.current_level)
        elif self.state == Elevator.MOVING:
            return "Elevator " + str(self.name) + " MOVING to " + str(self.next_stop[0].level)
        elif self.state == Elevator.DOORS_OPEN:
            return "Elevator " + str(self.name) + " DOORS OPEN at " + str(self.current_level)
        else:
            return "Elevator " + str(self.name) + ": " + str(self.state) + " ?"

# end class Elevator


class ElevatorStatistics (SimulatorObject):
    '''The ElevatorStatistics object watches several elevators and collects
    statistics about how much time they spend being active and idle. It is
    a SimulatorObject because the statistics object needs to be notified
    when the simulation run begins and ends. The print_summary method is
    called after the end of a run to print out summary statistics.'''
    def __init__(self, simulator):
        SimulatorObject.__init__(self, simulator)
        self.clock = simulator
        self.elevators = {}

    def update(self, obj):
        '''Callback method for when a watched elevator notifies of a state
        change.'''
        assert isinstance(obj, Elevator)
        if obj.name not in self.elevators:
            self.elevators[obj.name] = { 'state' : obj.state,
                                         'last_switch' : self.clock.get_time(),
                                         'total_active' : 0.0,
                                         'total_idle' : 0.0 }
            return
        if obj.state == Elevator.IDLE:
            assert self.elevators[obj.name]['state'] != Elevator.IDLE
            if self.elevators[obj.name]['state'] != Elevator.IDLE:
                now = self.clock.get_time()
                delta = now - self.elevators[obj.name]['last_switch']
                #print("DEBUG: delta =", delta, "now =", now)
                self.elevators[obj.name]['total_active'] += delta
                self.elevators[obj.name]['last_switch'] = now
        elif self.elevators[obj.name]['state'] == Elevator.IDLE:
            now = self.clock.get_time()
            delta = now - self.elevators[obj.name]['last_switch']
            #print("DEBUG: delta =", delta, "now =", now)
            self.elevators[obj.name]['total_idle'] += delta
            self.elevators[obj.name]['last_switch'] = now
        self.elevators[obj.name]['state'] = obj.state

    def end_run(self, end_time):
        '''Callback method for the end of a simulator run.'''
        for (name, stats) in self.elevators.items():
            delta = end_time - stats['last_switch']
            if stats['state'] == Elevator.IDLE:
                stats['total_idle'] += delta
            else:
                stats['total_active'] += delta

    def print_summary(self):
        '''Print a summary of collected elevator statistics.'''
        for (name, stats) in self.elevators.items():
            active_time = stats['total_active']
            idle_time = stats['total_idle']
            total_time = active_time + idle_time
            print("Elevator {}: Active {:.1f} ({:.2f}%), Idle {:.1f} ({:.2f}%)".format(name, active_time, (active_time/total_time) * 100, idle_time, (idle_time/total_time) * 100))

# end class ElevatorStatistics


class Floor (Observable):
    '''The Floor class represents a floor in the building. It is not an
    active simulator object (does not schedule events) but keeps track
    of lists of passengers (Passenger objects) waiting to go up and down.
    The constructor argument 'level' is the number of the floor (starting
    from 0 at ground and counting up).'''
    def __init__(self, level):
        Observable.__init__(self)
        self.level = level
        
    def reset(self):
        '''Called to reset the floor state at the start of a simulator
        run. Clears the waiting lists.'''
        self.waiting_to_go_up = []
        self.waiting_to_go_down = []
        self.notify()

    def get_passengers_entering(self, direction, free_space):
        '''Called by an Elevator when it stops at this Floor. Returns
        a list of Passengers going in 'direction', of length no more
        than 'free_space'.'''
        entering = []
        # If the direction indicated by the elevator is not down (i.e.,
        # it is either up, or no direction), passengers waiting to go
        # up may enter:
        if direction == DIR_UP or direction == DIR_NONE:
            if len(self.waiting_to_go_up) > 0:
                while len(self.waiting_to_go_up) > 0 and free_space > 0:
                    next_passenger = self.waiting_to_go_up.pop(0)
                    entering.append(next_passenger)
                    free_space -= 1
            if len(self.waiting_to_go_up) > 0:
                self.call_direction = DIR_UP
        # Likewise, if the direction indicated by the elevator is not up
        # (i.e., it is either down, or no direction), passengers waiting
        # to go down may enter:
        if direction == DIR_DOWN or direction == DIR_NONE:
            if len(self.waiting_to_go_down) > 0:
                while len(self.waiting_to_go_down) > 0 and free_space > 0:
                    next_passenger = self.waiting_to_go_down.pop(0)
                    entering.append(next_passenger)
                    free_space -= 1
            if len(self.waiting_to_go_down) > 0:
                self.call_direction = DIR_DOWN
        # If state has changed, notify watchers:
        if len(entering) > 0:
            self.notify()
        return entering

    def add_waiting_passenger(self, passenger):
        '''Called by TrafficGenerator objects when a new waiting passenger
        at this floor is created.'''
        self.call_direction = DIR_NONE
        if passenger.destination > self.level:
            if len(self.waiting_to_go_up) == 0:
                self.call_direction = DIR_UP
            self.waiting_to_go_up.append(passenger)
            passenger.arrive()
        elif passenger.destination < self.level:
            if len(self.waiting_to_go_up) == 0:
                self.call_direction = DIR_DOWN
            self.waiting_to_go_down.append(passenger)
            passenger.arrive()
        # Notify watchers that state of the Floor has changed:
        self.notify()


class Dispatcher (SimulatorObject):
    '''The Dispatcher class implements the other half of the elevator
    control strategy, by dispatching calls for an elevator (made from
    floors) to an appropriate elevator. It does this in two ways: when
    a call is made, if there is an idle elevator that can respond to
    it, the call is dispatched immediately. Otherwise, it is placed on
    a waiting list, and will be returned to the next (suitable) elevator
    that invokes the get_pickup method.
    Constructor arguments are:
    elevators - a list of Elevator objects. The dispatcher will inform
      each elevator object in the list that it is controlled by this
      dipatcher.
    floors - a list of Floor objects, ordered by level (0, .., #floors-1).
    '''
    def __init__(self, elevators, floors, simulator):
        SimulatorObject.__init__(self, simulator)
        self.elevators = elevators
        for elevator in elevators:
            elevator.set_dispatcher(self)
        self.floors = floors
        for floor in floors:
            floor.add_watcher(self)

    def start_run(self, start_time):
        '''Callback for the start of a simulation run. Reset waiting
        call list to empty, and call reset on all floors.'''
        self.waiting_calls = []
        for floor in self.floors:
            floor.reset()

    def update(self, obj):
        '''Callback for state updates from Floor objects.'''
        level = obj.level
        try:
            if obj.call_direction != DIR_NONE:
                self.call(level, obj.call_direction)
        # An AttributeError will be raised if the (Floor) object
        # does not have a call_direction set; this can happen when
        # when the floors are initialised.
        except AttributeError:
            pass
        obj.call_direction = DIR_NONE

    def call(self, level, direction):
        '''Internal helper method to handle a call for an elevator.'''
        # If there is an idle elevator, dispatch the call directly:
        for elevator in self.elevators:
            if elevator.state == Elevator.IDLE:
                elevator.dispatch(level, direction)
                return
        # Otherwise, place the call on the waiting list:
        self.waiting_calls.append((level, direction))

    def get_pickup(self, level, next_level = None, next_direction = DIR_NONE):
        '''Method called by an elevator after it has closed doors. The
        parameters next_level and next_direction are the elevators
        currently scheduled next stop; this method returns a new tuple
        (next_level, next_direction), which may either be the same or
        a different one.'''
        # If there are no waiting calls, the elevator can proceed with
        # its planned next stop.
        if len(self.waiting_calls) == 0:
            return (next_level, next_direction)
        # If next_level == None, the elevator is not en route anywhere,
        # so we just give it the first waiting call:
        if next_level == None:
            first_waiting_call = self.waiting_calls.pop(0)
            return first_waiting_call
        # Else, if there is a waiting call between level and next_level,
        # with matching direction, we can insert it:
        for i in range(len(self.waiting_calls)):
            (call_level, call_dir) = self.waiting_calls[i]
            if level < call_level < next_level and call_dir == DIR_UP:
                self.waiting_calls.pop(i)
                return (call_level, call_dir)
            elif level > call_level > next_level and call_dir == DIR_DOWN:
                self.waiting_calls.pop(i)
                return (call_level, call_dir)
        # Otherwise, return the arguments:
        return (next_level, next_direction)

# end class Dispatcher


class Passenger (Observable):
    '''Object representing a passenger. Passenger objects are passive
    (do not schedule events), and exist mainly as a place to store the
    time when the passenger arrived (began waiting), boarded and exited
    an elevator.'''
    CREATED = 0
    WAITING = 1
    TRAVELLING = 2
    SERVED = 3

    # Passenger.logs is a class-wide list of objects that will watch
    # all passengers. When a new Passenger is created, each object in
    # this list will be added as a watcher of the passenger.
    logs = []

    def __init__(self, orig, dest):
        Observable.__init__(self)
        assert orig != dest
        self.origin = orig
        self.destination = dest
        self.state = Passenger.CREATED
        # Add watchers to the new passenger:
        for log in Passenger.logs:
            self.add_watcher(log)

    def arrive(self):
        '''Called when the passenger is placed in the waiting list at
        her origin floor.'''
        self.state = Passenger.WAITING
        self.notify()

    def board(self):
        '''Called when the passenger boards an elevator.'''
        self.state = Passenger.TRAVELLING
        self.notify()

    def exit(self):
        '''Called when the passenger exits an elevator at her destination
        floor.'''
        self.state = Passenger.SERVED
        self.notify()

    def id_string(self):
        return "Passenger " + str(self.origin) + " -> " + str(self.destination)

    def __str__(self):
        '''Returns a string describing the state of the passenger.'''
        if self.state == Passenger.WAITING:
            return self.id_string() + " waiting"
        elif self.state == Passenger.TRAVELLING:
            return self.id_string() + " travelling"
        elif self.state == Passenger.SERVED:
            return self.id_string() + " served"
        else:
            return self.id_string() + " " + str(self.state) + " ?"

# end class Passenger


class PassengerStatistics (object):
    '''The PassengerStatistics object records statistics about passengers.
    The print_summary method is called to print statistics after the end
    of a simulator run. The clock argument to the constructor should be
    a GlobalClock (i.e., the simulator), and is used to get event time.'''
    def __init__(self, clock):
        self.clock = clock
        self.currently_waiting = 0
        self.currently_travelling = 0
        self.peak_waiting = 0
        self.peak_travelling = 0
        self.total_wait_time = 0
        self.total_wait_count = 0
        self.total_travel_time = 0
        self.total_travel_count = 0

    def update(self, obj):
        '''Callback for when the state of a passenger has changed.'''
        assert isinstance(obj, Passenger)
        if obj.state == Passenger.WAITING:
            obj.begin_waiting_time = self.clock.get_time()
            self.currently_waiting += 1
            if self.currently_waiting > self.peak_waiting:
                self.peak_waiting = self.currently_waiting
        elif obj.state == Passenger.TRAVELLING:
            obj.begin_travelling_time = self.clock.get_time()
            wait_time = obj.begin_travelling_time - obj.begin_waiting_time
            assert self.currently_waiting > 0
            self.currently_waiting -= 1
            self.currently_travelling += 1
            if self.currently_travelling > self.peak_travelling:
                self.peak_travelling = self.currently_travelling
            self.total_wait_time += wait_time
            self.total_wait_count += 1
        elif obj.state == Passenger.SERVED:
            obj.end_travelling_time = self.clock.get_time()
            travel_time = obj.end_travelling_time - obj.begin_travelling_time
            assert self.currently_travelling > 0
            self.currently_travelling -= 1
            self.total_travel_time += travel_time
            self.total_travel_count += 1

    def print_summary(self):
        '''Print summary of passenger statistics.'''
        print("Total number of passengers served: {}".format(self.total_travel_count))
        print("Passengers in system at end of run: {} waiting, {} travelling".format(self.currently_waiting, self.currently_travelling))
        print("Peak number of passengers waiting:", self.peak_waiting)
        print("Peak number of passengers in transit:", self.peak_travelling)
        if self.total_wait_count > 0:
            print("Average waiting time: {:.2f}".format(self.total_wait_time / self.total_wait_count))
        if self.total_travel_count > 0:
            print("Average travel time: {:.2f}".format(self.total_travel_time / self.total_travel_count))

# end class PassengerStatistics
            

class PrintEvents (object):
    '''A PrintEvents object is a monitor that can watch objects and
    print a message every time their state is updated. It is used only
    to provide verbose output from the simulation. The clock argument
    to the constructor should be a GlobalClock, and is used to get
    event time.'''
    def __init__(self, clock):
        self.clock = clock

    def update(self, obj):
        print("{:.1f} : {}".format(self.clock.get_time(), str(obj)))

# end class PrintEvents


class UniformTrafficGenerator (SimulatorObject):
    '''A traffic generator is an active simulator object that generates
    randomly new passengers. The UniformTrafficGenerator selects origin
    and destination floors uniformly at random, and schedules passenger
    arrivals with a specified mean interval. Constructor arguments are:
    floors - The list of Floors in the building, ordered by level
      (0 .. #floors - 1).
    mean_time (float) - The average time between passenger arrivals,
      in seconds.
    simulator - The simulator.'''
    def __init__(self, floors, mean_time, simulator):
        SimulatorObject.__init__(self, simulator)
        self.floors = floors
        self.set_mean_time(mean_time)
        self.random = Random()

    def set_mean_time(self, mean_time):
        '''Set (change) the mean time between passenger arrivals.'''
        assert mean_time > 0
        self.lambd = 1/mean_time

    def choose_origin_and_destination(self):
        '''Internal helper method to select random origin and destination
        floors. Should return a tuple of two integers, which MUST NOT be
        equal.'''
        orig = int(self.random.uniform(0, len(self.floors) - 1))
        dest = int(self.random.uniform(0, len(self.floors) - 1))
        while dest == orig:
            dest = int(self.random.uniform(0, len(self.floors) - 1))
        return (orig, dest)

    def start_run(self, start_time):
        '''Callback for the start of a simulator run. Schedules the
        first passenger arrival.'''
        dt = self.random.expovariate(self.lambd)
        self.schedule_next_event(dt, self.create_passenger)

    def create_passenger(self):
        '''Callback for when a new passenger arrives. This method
        creates the passenger, adds her to her origin floor, and
        schedules the next passenger arrival.'''
        (origin, destination) = self.choose_origin_and_destination()
        assert origin != destination
        new_passenger = Passenger(origin, destination)
        self.floors[origin].add_waiting_passenger(new_passenger)
        dt = self.random.expovariate(self.lambd)
        self.schedule_next_event(dt, self.create_passenger)

# end class UniformTrafficGenerator
