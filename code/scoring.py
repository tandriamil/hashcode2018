#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hash code 2018.

A module whose objective is to simulate the scoring but it does not.
"""
import csv
import sys

import numpy as np

from code.hashcode import B_INPUT_FILE, parse_input


class ProgrammedRide(object):

    def __init__(self, vehicle_id, line):
        self.vehicle_id = vehicle_id
        self.nb_rides = int(line[0])
        self.rides = [int(ride) for ride in line[1:]]

    def __str__(self):
        ret_str = 'Vehicle %d has %d rides: [' % (
            self.vehicle_id, self.nb_rides)
        ret_str += ', '.join(['%d' % ride for ride in self.rides])
        ret_str += ']'
        return ret_str


class SimulatedWorld(object):

    def __init__(self, world, programmed_rides):
        self.score = 0
        self.word = world
        self.programmed_rides = programmed_rides

    def process(self):
        for vehicle_id, ride in enumerate(programmed_rides):
            print('Vehicle number %d:' % vehicle_id)
            curr_sim_ride = SimulatedRide(
                self.word.rides, self.word.bonus_points, ride)
            curr_sim_ride.process()
            self.score += curr_sim_ride.score


class SimulatedRide(object):

    def __init__(self, rides, early_bonus, programmed_rides):
        self.rides = rides
        self.early_bonus = early_bonus
        self.nb_rides = programmed_rides.nb_rides
        self.prog_rides = programmed_rides.rides
        self.next_ride = 0
        self.curr_pos = (0, 0)
        self.curr_date = 0
        self.score = 0

    def process(self):
        while self.next_ride < self.nb_rides:
            bonus_yeah = 0

            # Prepare the next ride
            ride_id = self.prog_rides[self.next_ride]
            curr_ride = self.rides[ride_id]
            print('Ride %d at time %d is%s' % (
                ride_id, self.curr_date, curr_ride))

            # Move the car to the departure
            dist_from_departure = sum((
                np.abs(self.curr_pos[0] - curr_ride.start_row),
                np.abs(self.curr_pos[1] - curr_ride.start_col)))
            self.curr_date += dist_from_departure

            # If early arrival
            if self.curr_date <= curr_ride.earliest_start:
                self.curr_date = curr_ride.earliest_start
                bonus_yeah += self.early_bonus

            # Move the car (position and time both evolved)
            dist_to_arrival = sum((
                np.abs(self.curr_pos[0] - curr_ride.finish_row),
                np.abs(self.curr_pos[1] - curr_ride.finish_col)))
            self.curr_pos = (curr_ride.finish_row, curr_ride.finish_col)
            self.curr_date += dist_to_arrival

            # Update the score (add bonus if got)
            self.score += bonus_yeah + dist_to_arrival
            print('Current score: %d' % self.score)
            print()

            self.next_ride += 1


def parse_submission(input_file_path):
    programmed_rides = []
    with open(input_file_path) as input_file:
        csv_reader = csv.reader(input_file, delimiter=' ')
        for vehicle_id, line in enumerate(csv_reader):
            programmed_rides.append(ProgrammedRide(vehicle_id, line))

    print('%d programmed rides parsed:' % (programmed_rides[0].nb_rides))
    for prog_ride in programmed_rides:
        print(prog_ride)
    print()

    return programmed_rides


if __name__ == '__main__':
    programmed_rides = parse_submission(sys.argv[1])
    world = parse_input('B_WORLD', B_INPUT_FILE)
    sim_world = SimulatedWorld(world, programmed_rides)
    sim_world.process()
    score = sim_world.score

    print('KIIILLL MEEEEEEEEEEEEE')

    print('Score of %d !!!' % score)
