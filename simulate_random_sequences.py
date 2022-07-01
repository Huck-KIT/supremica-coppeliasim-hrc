import b0RemoteApi
import random
import time
import csv
import Environment
from xml.dom.minidom import parse, Node

########################## Simulation Settings #################################
scenario = 1 # Currently available: {1,2}
use_random_parameters = True
n_simulation_runs = 960
log_results = True

####################### Load scenario parameters ###############################
if scenario == 1:
    motionParametersMin = [-0.2,0.8, 1]
    motionParametersMax = [0.2, 1.2, 1.5]
    motionParametersNominal = [0,1,1]
    automaton_filepath = "models/supremica/XML/human_model_scenario_A.xml"
    action_sequence_filepath="models/supremica/CSV/action_sequences_human_model_scenario_A.csv"
    results_filepath = "results/results_random_scenario_A.csv"
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

with b0RemoteApi.RemoteApiClient('b0RemoteApi_V-REP-addOn','b0RemoteApiAddOn') as client:  #This line defines the client, which provides all functions of the remote API
    # create and initialize simution environment
    env = Environment.Environment(client,motionParametersMin,motionParametersMax,motionParametersNominal,automaton_filepath)
    env.sim_start()
    # sample random action sequence and parameters
    for i in range(n_simulation_runs):
        print("simulation run "+str(i+1)+ " of "+str(n_simulation_runs))
        random_sequence = random.choice(action_sequences)
        print("random sequence: ")
        print(random_sequence)
        assert env.workflow_check_acceptance(random_sequence), "sequence not accepted"
        random_params = list()
        for j in range(len(motionParametersMin)):
            random_params.append(motionParametersMin[j] + (motionParametersMax[j]-motionParametersMin[j])*random.random())
        print("random parameters:")
        print(random_params)
        # simulate the sequence
        current_max_risk = 0
        for current_action in random_sequence:
            risk = env.sim_step(current_action,random_params)
            if risk > current_max_risk:
                current_max_risk = risk
        # log the results and reset the simulator
        sequence_log.append(random_sequence)
        parameter_log.append(random_params)
        risk_log.append(current_max_risk)
        print("Risk logged: "+str(current_max_risk))
        env.sim_reset()
    env.sim_stop()
