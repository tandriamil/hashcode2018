#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hash code 2018.

Runner of the simulations. Submissions files will be put into the named dir.
"""
import os
from code.hashcode import Simulation

CHALLENGES = ['a_example', 'b_should_be_easy', 'c_no_hurry',
              'd_metropolis', 'e_high_bonus']

for challenge in CHALLENGES:
    print('##### Executing simulation %s #####' % challenge)
    input_filename = os.path.join('datas', '%s.in' % challenge)
    simulation = Simulation(input_filename)
    simulation.launch_simulation()
    simulation.submit()
