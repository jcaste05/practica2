"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value


SOUTH = 1
NORTH = 0
PED = 2

NCARS = 20
NPED = 5
TIME_CARS_NORTH = 2  # a new car enters each 0.5s
TIME_CARS_SOUTH = 2  # a new car enters each 0.5s
TIME_PED = 10 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (2, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (12, 2) # normal 30s, 10s

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.patata = Value('i', 0)
        self.ncochesN = Value('i', 0)
        self.ncochesS = Value('i', 0)
        self.nped = Value('i', 0)
        self.turn = Value('i', NORTH)
        self.Nwaiting = Value('i', 0)
        self.Swaiting = Value('i', 0)
        self.Pwaiting = Value('i', 0)
        self.no_S_P = Condition(self.mutex)
        self.no_N_P = Condition(self.mutex)
        self.no_N_S = Condition(self.mutex)
        
    def are_no_S_P(self):
        return (self.ncochesS.value + self.nped.value == 0) and (self.turn.value == NORTH or (self.Swaiting.value + self.Pwaiting.value == 0))
    
    def are_no_N_P(self):
        return (self.ncochesN.value + self.nped.value == 0) and (self.turn.value == SOUTH or (self.Nwaiting.value + self.Pwaiting.value == 0))
    
    def are_no_N_S(self):
        return (self.ncochesN.value + self.ncochesS.value == 0) and (self.turn.value == PED or (self.Nwaiting.value + self.Swaiting.value == 0))

    def wants_enter_car(self, direction: int) -> None: #Hecho
        self.mutex.acquire()
        self.patata.value += 1
        if direction == NORTH:
            self.Nwaiting.value += 1
            self.no_S_P.wait_for(self.are_no_S_P)
            self.Nwaiting.value -= 1
            self.ncochesN.value += 1
        else:
            self.Swaiting.value += 1
            self.no_N_P.wait_for(self.are_no_N_P)
            self.Swaiting.value -= 1
            self.ncochesS.value += 1
        self.mutex.release()

    def leaves_car(self, direction: int) -> None: #Hecho
        self.mutex.acquire() 
        self.patata.value += 1
        if direction == NORTH:
            self.ncochesN.value -= 1
            if self.Swaiting.value > 0: #Si hay gente en el sur esperando cedo el turno
                self.turn.value = SOUTH
            else: #Si no, se lo cedo a los peatones
                self.turn.value = PED
            if self.ncochesN.value == 0:
                self.no_N_P.notify_all()
                self.no_N_S.notify_all()
        else:
            self.ncochesS.value -= 1
            if self.Pwaiting.value > 0:
                self.turn.value = PED
            else:
                self.turn.value = NORTH
            if self.ncochesS.value == 0:
                self.no_N_S.notify_all()
                self.no_S_P.notify_all()
        self.mutex.release()

    def wants_enter_pedestrian(self) -> None: #Hecho
        self.mutex.acquire()
        self.patata.value += 1
        self.Pwaiting.value += 1
        self.no_N_S.wait_for(self.are_no_N_S)
        self.Pwaiting.value -= 1
        self.nped.value += 1
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        self.nped.value -= 1
        if self.Nwaiting.value > 0: 
            self.turn.value = NORTH
        else:
            self.turn.value = SOUTH
        if self.nped.value == 0:
            self.no_S_P.notify_all()
            self.no_N_P.notify_all()
        self.mutex.release()

    def __repr__(self) -> str:
        return f'Monitor: {self.patata.value}'

def delay_car_north() -> None:
    num_al = random.gauss(TIME_IN_BRIDGE_CARS[0], TIME_IN_BRIDGE_CARS[1])
    if num_al <= 0:
        num_al = 0.01
    time.sleep(num_al)

def delay_car_south() -> None:
    num_al = random.gauss(TIME_IN_BRIDGE_CARS[0], TIME_IN_BRIDGE_CARS[1])
    if num_al <= 0:
        num_al = 0.01
    time.sleep(num_al)

def delay_pedestrian() -> None:
    num_al = random.gauss(TIME_IN_BRIDGE_PEDESTRIAN[0], TIME_IN_BRIDGE_PEDESTRIAN[1])
    if num_al <= 0:
        num_al = 0.01
    time.sleep(num_al)

def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction==NORTH :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")



def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))

    for p in plst:
        p.join()

def gen_cars(direction: int, time_cars, monitor: Monitor) -> None:
    cid = 0
    plst = []
    for _ in range(NCARS):
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/time_cars))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars_north = Process(target=gen_cars, args=(NORTH, TIME_CARS_NORTH, monitor))
    gcars_south = Process(target=gen_cars, args=(SOUTH, TIME_CARS_SOUTH, monitor))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars_north.start()
    gcars_south.start()
    gped.start()
    gcars_north.join()
    gcars_south.join()
    gped.join()


if __name__ == '__main__':
    main()
