import b0RemoteApi
import random
import time
import csv
import Environment
from xml.dom.minidom import parse, Node

########################## Simulation Settings #################################
scenario = 3 # Currently available: {1,2}
use_random_parameters = True
trigger_actions_manually = False
n_simulation_runs = 500
log_results = True

############################ Run Simulations ###################################
with b0RemoteApi.RemoteApiClient('b0RemoteApi_V-REP-addOn','b0RemoteApiAddOn') as client:  #This line defines the client, which provides all functions of the remote API

    for seed in range(8,10):

        random.seed(seed)

        ########################## Load parameters #################################

        if seed < 10:
            path_appendix = "_0"+str(seed)
        else:
            path_appendix = "_"+str(seed)

        if scenario == 1:
            motionParametersMin = [-0.2,0.8, 1]
            motionParametersMax = [0.2, 1.2, 1.5]
            motionParametersNominal = [0, 1, 1]
            automaton_filepath = "models/supremica/XML/human_model_scenario_A.xml"
            action_sequence_filepath="models/supremica/CSV/action_sequences_human_model_scenario_A.csv"
            results_filepath = "results/results_random_scenario_A.csv"
        elif scenario == 2:
            motionParametersMin = [0.7, -0.1, -0.1]
            motionParametersMax = [1.3, 0, 0.1]
            motionParametersNominal = [1, 0, 0]
            automaton_filepath = "models/supremica/XML/human_model_scenario_B.xml"
            action_sequence_filepath="models/supremica/CSV/action_sequences_human_model_scenario_B.csv"#action_sequences_supervisor_scenario_B.csv"#
            results_filepath = "results/results_random_scenario_B.csv"
        elif scenario == 3:
            motionParametersMin = [-0.2,0.8, 1]
            motionParametersMax = [0.2, 1.2, 1.5]
            motionParametersNominal = [0, 1, 1]
            automaton_filepath = "models/supremica/XML/human_model_scenario_C.xml"
            action_sequence_filepath="models/supremica/CSV/action_sequences_human_model_scenario_C.csv"
            results_filepath = "results/results_random_scenario_C_"+path_appendix+".csv"
        elif scenario == 4:
            motionParametersMin = [-0.2,0.8, 1]
            motionParametersMax = [0.2, 1.2, 1.5]
            motionParametersNominal = [0, 1, 1]
            automaton_filepath = "models/supremica/XML/human_model_scenario_C.xml"
            action_sequence_filepath="models/supremica/CSV/action_sequences_human_model_scenario_C.csv"
            results_filepath = "results/results_random_scenario_D.csv"
        elif scenario == 5:
            motionParametersMin = [-0.2,0.8, 1]
            motionParametersMax = [0.2, 1.2, 1.5]
            motionParametersNominal = [0, 1, 1]
            automaton_filepath = "models/supremica/XML/human_model_scenario_C.xml"
            action_sequence_filepath="models/supremica/CSV/action_sequences_human_model_scenario_C.csv"
            results_filepath = "results/results_random_scenario_E.csv"
        elif scenario == 6:
            motionParametersMin = [-0.2,0.8, 1]
            motionParametersMax = [0.2, 1.2, 1.5]
            motionParametersNominal = [0, 1, 1]
            automaton_filepath = "models/supremica/XML/human_model_scenario_C.xml"
            action_sequence_filepath="models/supremica/CSV/action_sequences_human_model_scenario_C.csv"
            results_filepath = "results/results_random_scenario_F"+path_appendix+".csv"
        else:
            "Error! Select valid scenario number (1 or 2) in line 9!"


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

            # create and initialize simution environment
            env = Environment.Environment(client,motionParametersMin,motionParametersMax,motionParametersNominal,automaton_filepath,trigger_actions_manually)
            env.sim_start()
            # sample random action sequence and parameters
            for i in range(n_simulation_runs):
                print("seed: "+str(seed))
                print("simulation run "+str(i+1)+ " of "+str(n_simulation_runs))
                random_sequence = random.choice(action_sequences)
                print("random sequence: ")
                print(random_sequence)
                assert env.workflow_check_acceptance(random_sequence), "sequence not accepted"
                current_parameters = list()
                if use_random_parameters:
                    for j in range(len(motionParametersMin)):
                        current_parameters.append(motionParametersMin[j] + (motionParametersMax[j]-motionParametersMin[j])*random.random())
                else:
                    current_parameters = env.sim_params_nominal

                # simulate the sequence
                current_max_risk = 0
                logged_sequence = list()
                for current_action in random_sequence:
                    logged_sequence.append(current_action)
                    risk = env.sim_step(current_action,current_parameters)
                    if risk > current_max_risk:
                        current_max_risk = risk
                    if current_max_risk > 1:
                        break

                # log the results and reset the simulator
                sequence_log.append(logged_sequence)
                parameter_log.append(current_parameters)
                risk_log.append(env.get_max_risk())# was: risk_log.append(current_max_risk)
                env.sim_reset()


        if log_results:
            with open(results_filepath, 'w', newline='') as csvfile:
                fieldnames = ['sequence', 'param', 'risk']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for i in range(len(sequence_log)):
                    writer.writerow({fieldnames[0]: sequence_log[i], fieldnames[1]: parameter_log[i], fieldnames[2]:risk_log[i]})

    env.sim_stop()
