"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
simulate_supervisor_sequences.py

Author: Tom P. Huck
Karlsruhe Institute of Technology (KIT), Karlsruhe, Germany
Date: 2022-01-15

This script simualtes action sequences which were previously generated through
supervisor synthesis in supremica and saved at 'action_sequence_filepath.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

import b0RemoteApi
import random
import time
import csv
import Environment
from xml.dom.minidom import parse, Node

########################## Simulation Settings #################################
scenario = 2 # Currently available: {1,2}
repetitions_per_sequence = 22
max_sequence_length = 11 #sequence length expressed as number of actions
use_random_parameters = True
log_results = True
trigger_actions_manually = False
random.seed(7)
####################### Load scenario parameters ###############################

if scenario == 1:
    motionParametersMin = [-0.2,0.8, 1]
    motionParametersMax = [0.2, 1.2, 1.5]
    motionParametersNominal = [0,1,1]
    automaton_filepath = "models/supremica/XML/supervisor_scenario_A.xml"
    action_sequence_filepath="models/supremica/CSV/action_sequences_supervisor_scenario_A.csv"
    results_filepath = "results/results_supervisor_scenario_A.csv"
elif scenario == 2:
    motionParametersMin = [0.7, -0.1, -0.1]
    motionParametersMax = [1.3, 0, 0.1]
    motionParametersNominal = [1,0,0]
    automaton_filepath = "models/supremica/XML/supervisor_scenario_B.xml"
    action_sequence_filepath="models/supremica/CSV/action_sequences_supervisor_scenario_B.csv"
    results_filepath = "results/results_supervisor_scenario_B.csv"
else:
    "Error! Select valid scenario number (1) in line 9!"

############################ Run Simulations ###################################
# initialize logs
action_sequences = list()
sequence_log = list()
parameter_log = list()
risk_log = list()

# load pre-computed action sequences
with open(action_sequence_filepath, newline='') as csvfile:
    print("load action sequences...")
    reader_obj = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader_obj:
        action_sequences.append(row)
    print(str(len(action_sequences))+" sequences loaded.")

    print("remove sequences which are above maximum length...:")
    sequences_length_limited = list()
    for sequence in action_sequences:
        print(sequence)
        print("len: "+str(len(sequence)))
        if len(sequence) > max_sequence_length+1:
            print("remove!")
            # action_sequences.remove(sequence)
        else:
            print("keep!")
            sequence.remove('collision')
            sequences_length_limited.append(sequence)

    print(str(len(sequences_length_limited))+" remaining:")
    for sequence in sequences_length_limited:
        print(sequence)
        print("len: "+str(len(sequence)))


# simulate action sequences
with b0RemoteApi.RemoteApiClient('b0RemoteApi_V-REP-addOn','b0RemoteApiAddOn') as client:  #This line defines the client, which provides all functions of the remote API
    env = Environment.Environment(client,motionParametersMin,motionParametersMax,motionParametersNominal,automaton_filepath,trigger_actions_manually)
    env.print_action_space()
    env.sim_start()
    sequence_counter = 0
    for current_action_sequence in sequences_length_limited:
        assert env.workflow_check_acceptance(current_action_sequence), "Sequence not accepted by supervisor automaton!"
        sequence_counter+=1
        for repetition_counter in range(repetitions_per_sequence):
            current_max_risk = 0
            print("simulate sequence "+str(sequence_counter)+" of "+str(len(sequences_length_limited)))
            print("repetition "+str(repetition_counter+1)+ " of "+str(repetitions_per_sequence))
            print(current_action_sequence)
            # sample motion parameters for this sequence
            if use_random_parameters:
                current_parameters = list() # use default parameters
                for i in range(3):
                    current_parameters.append(env.sim_params_min[i]+(env.sim_params_max[i]-env.sim_params_min[i])*random.random())
                print("parameters selected:")
                print(current_parameters)
            else:
                current_parameters = env.sim_params_nominal # use default parameters
            for current_action in current_action_sequence:
                risk = env.sim_step(current_action,current_parameters)
                if risk > current_max_risk:
                    current_max_risk = risk
            print("sequence done!")
            sequence_log.append(current_action_sequence)
            parameter_log.append(current_parameters)
            risk_log.append(current_max_risk)
            print("Risk logged: "+str(current_max_risk))
            env.sim_reset()

    env.sim_stop()

    # log results
    if log_results:
        with open(results_filepath, 'w', newline='') as csvfile:
            fieldnames = ['sequence', 'param', 'risk']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(len(sequence_log)):
                writer.writerow({fieldnames[0]: sequence_log[i], fieldnames[1]: parameter_log[i], fieldnames[2]:risk_log[i]})
