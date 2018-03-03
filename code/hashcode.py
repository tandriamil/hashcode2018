#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hash code 2018.

Main module, contains the structures and the whole process.
"""
import csv
import itertools
import os
import numpy as np

THRESHOLD_DANGEROUS = 420  # blaze it

class Car(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rides = []
        self.T_free = 0
        self.current_ride = None

    def set_T_free(self, T, ride, delay=True):
        if not delay:
            self.T_free = T + self.d_to_ride(ride) + ride.distance
        else:
            Tdepart = T + self.d_to_ride(ride)
            Dd = 0
            if(Tdepart < ride.earliest_start):
                Dd = ride.earliest_start - Tdepart
            self.T_free = T + Tdepart + Dd + ride.distance

    def d_to_ride(self, r):
        return np.abs(self.x - r.start_row) + np.abs(self.y - r.start_col)


class Ride(object):

    def __init__(self, ride_line, id):
        self.start_row = int(ride_line[0])
        self.start_col = int(ride_line[1])
        self.finish_row = int(ride_line[2])
        self.finish_col = int(ride_line[3])
        self.earliest_start = int(ride_line[4])
        self.latest_finish = int(ride_line[5])
        self.distance = np.abs(self.start_row - self.finish_row) + np.abs(self.start_col - self.finish_col)
        self.latest_start = self.latest_finish - self.distance
        self.affectation = 0
        self.id = id
        # 1 affecte
        # 0 non affecte
        # -1 mort

    def __str__(self):
        return '  Ride %d: Start at (%d, %d), finish at (%d, %d), time window (%d, %d)' % (
            self.id, self.start_row, self.start_col, self.finish_row, self.finish_col,
            self.earliest_start, self.latest_finish)


class World(object):

    def __init__(self, name, first_line):
        self.name = name.split('/')[-1]
        self.nb_rows = int(first_line[0])
        self.nb_cols = int(first_line[1])
        self.nb_cars = int(first_line[2])
        self.nb_rides = int(first_line[3])
        self.bonus_points = int(first_line[4])
        self.nb_steps = int(first_line[5])
        self.rides = []
        self.cars = []

    def test_possible_rides(self, T):
        for r in self.rides:
            if(r.affectation == 0):
                for c in self.cars:
                    if(c.T_free >= T + c.d_to_ride(r)):
                        i = 0

    def get_unaffected_rides(self):
        rides = (r for r in self.rides if r.affectation == 0)
        return list(itertools.islice(rides,0,4*self.nb_cars))

    def shoot_ride(self, r):
        self.rides.remove(r)

    def add_car(self):
        self.cars.append(Car(0,0))

    def add_ride(self, line, id):
        self.rides.append(Ride(line, id))

    def __str__(self):
        ret_str = 'World %s, %d steps, (%d x %d), %d vehicles and %d rides' % (
            self.name, self.nb_steps, self.nb_cols, self.nb_rows,
            self.nb_cars, self.nb_rides)
        for ride in self.rides:
            ret_str += '\n%s' % ride
        return ret_str

    @classmethod
    def create_from_file(cls, input_file_path):
        world = None
        world_name = os.path.splitext(input_file_path)[0]
        with open(input_file_path) as input_file:
            csv_reader = csv.reader(input_file, delimiter=' ')
            for r_id, line in enumerate(csv_reader):
                if world:
                    world.add_ride(line, r_id-1)
                else:
                    world = World(world_name, line)
            for n in range(world.nb_cars):
                world.add_car()
            world.rides.sort(key=lambda ride: ride.latest_start)
        return world


class Simulation(object):

    def __init__(self, input_file_path):
        self.world = World.create_from_file(input_file_path)
        self.input_filename = input_file_path

    def get_more_dangerous_rides(self, time, world, rides):
        if 'no_hurry' in self.input_filename:
            return []
        return [ride for ride in rides if ride.latest_start - time < THRESHOLD_DANGEROUS and ride.affectation != 1]

    def affect(self, car, ride, time):
        car.rides.append(ride)
        car.set_T_free(time, ride)
        car.x, car.y = ride.finish_row, ride.finish_col
        ride.affectation = 1

    def distance(self, pos_a, pos_b):
        x, y = pos_a
        x2, y2 = pos_b

        return abs(x - x2) + abs(y - y2)

    def get_closest_free_car(self, ride, cars, time):
        pos_ride = ride.start_row, ride.start_col
        min_dist = 9559819615165156
        best_car = None
        for car in cars:
            car_pos = (car.x, car.y)
            dist = self.distance(pos_ride, car_pos)
            if dist<min_dist:
                min_dist = dist
                best_car = car

        if min_dist+time>ride.latest_start:
            self.world.shoot_ride(ride)
            return None
        else:
            return best_car

    def get_free_cars(self, cars, time):
        return [car for car in cars if car.T_free <= time]

    def earning(self, car, ride, time):
        car_position = car.x, car.y
        ride_position = ride.start_row, ride.start_col
        dist = self.distance(car_position, ride_position)

        if dist+time>ride.latest_start:
            return -999999999

        waiting_time = max(0, ride.earliest_start - time - dist)
        return ride.distance / (dist + waiting_time)

    def choose_best_ride(self, car, rides, time):
        best_gain = -9999999999999
        best_ride = None
        for ride in rides:
            if ride.affectation == 1:
                continue
            gain = self.earning(car, ride, time)
            if gain > best_gain:
                best_gain = gain
                best_ride = ride
        return best_ride

    def submit(self):
        output_path = os.path.join(
            'submissions', '%s.out' % self.world.name)
        with open(output_path, 'w+') as output_file:
            for car in self.world.cars:
                number_rides = len(car.rides)
                output_file.write('%d ' % number_rides)
                for ride in car.rides:
                    output_file.write('%d ' % ride.id)
                output_file.write('\n')

    def launch_simulation(self):
        world = self.world
        world.cars = [Car(0, 0) for _ in range(world.nb_cars)]
        for time in range(world.nb_steps):
            rides = world.get_unaffected_rides()
            if time % 100 == 0:
                print('time = {} / {}'.format(time, world.nb_steps))
            for ride in self.get_more_dangerous_rides(time, world, rides):
                car = self.get_closest_free_car(ride, world.cars, time)
                if car:
                    self.affect(car, ride, time)
            for car in self.get_free_cars(world.cars, time):
                ride = self.choose_best_ride(car, rides, time)
                if ride:
                    self.affect(car, ride, time)
        print([[ride.id for ride in car.rides] for car in world.cars])


if __name__ == '__main__':
    simulation = Simulation('datas/b_should_be_easy.in')
    simulation.launch_simulation()
    simulation.submit()
