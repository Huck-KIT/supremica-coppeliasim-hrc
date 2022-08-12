"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
postprocessing.py

Author: Tom P. Huck
Karlsruhe Institute of Technology (KIT), Karlsruhe, Germany
Date: 2022-01-19

This script takes a *_results.csv file and evaluates:
- The average and maximum risk metric
- How many times a risk metric above a certain threshold has occured
- How many different action sequences have been found that lead to a risk
above the specified threshold.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import csv
import os
from Environment import Environment

verbose = False

def remove_separators_from_string(input_string):
        input_string = input_string.replace(",","")
        input_string = input_string.replace("'","")
        input_string = input_string.replace("\"","")
        input_string = input_string.replace("[","")
        input_string = input_string.replace("]","")
        return input_string

def check_supervisor_inclusion(simulation_action_sequences,supervisor_sequences_filepath):
    """ this function compares if the action sequences given by the list
    action_sequences are included in the action sequences obtained from the
    supervisor (given by the file at supervisor_file_path)"""

    #read in action sequences
    action_sequences_supervisor = list()
    with open(supervisor_sequences_filepath) as supervisor_csvfile:
        reader_obj = csv.reader(supervisor_csvfile, delimiter=',')
        for row in reader_obj:
            sequence_as_list = list()
            action_sequences_supervisor.append(row)

    # compare
    sequences_not_in_supervisor = list() # action sequences in simulation, but not in supervisor
    for input_sequence in simulation_action_sequences:
        # convert list into string for comparison
        input_sequence_as_list = input_sequence.split()
        # print("as list:")
        # print(input_sequence_as_list[0])
        if input_sequence_as_list[0] == "['initial',":
            del input_sequence_as_list[0] #remove 'initial' tag
        input_sequence_as_string = str(input_sequence_as_list)
        input_sequence_as_string = remove_separators_from_string(input_sequence_as_string)
        # print("compare with:")
        # print(action_sequences_supervisor)
        #compare with supervisor sequences
        supervisor_sequences_as_string = list()
        for supervisor_sequence in action_sequences_supervisor:
            supervisor_sequence_as_string = supervisor_sequence[0]#.remove('collision') # remove "collision" tag
            supervisor_sequence_as_list = supervisor_sequence_as_string.split()
            supervisor_sequence_as_list.remove("collision")
            supervisor_sequence_as_string = str(supervisor_sequence_as_list)
            supervisor_sequence_as_string = remove_separators_from_string(supervisor_sequence_as_string)
            supervisor_sequences_as_string.append(supervisor_sequence_as_string)
        if not (input_sequence_as_string in supervisor_sequences_as_string):
            sequences_not_in_supervisor.append(input_sequence_as_string)

    sequences_not_in_simulation = list() # action sequences in supervisor, but not in simulation
    for supervisor_sequence in action_sequences_supervisor:
        # print("compare: ")
        comp_string1 = supervisor_sequence[0].replace(" collision","")
        comp_string_list = list()
        for seq in simulation_action_sequences:
            comp_string2 = remove_separators_from_string(seq)
            if "initial " in comp_string2:
                comp_string2.replace("initial ","")
            comp_string_list.append(comp_string2)
        # print(comp_string1)
        # print(comp_string_list)
        if comp_string1 in comp_string_list:
            print("included!")
        else:
            print("not included")
            sequences_not_in_simulation.append(supervisor_sequence)
            print("seq not in simulation: "+str(len(sequences_not_in_simulation)))
    return sequences_not_in_supervisor,sequences_not_in_simulation


# results_filepath = os.getcwd()+"/results/results_mcts_scenario_A.csv"
supervisor_sequences_filepath = os.getcwd()+"/models/supremica/CSV/action_sequences_supervisor_scenario_B.csv"
#esults_filepath = os.getcwd()+"/results/Archive/results_random_scenario_B_04.csv"

search_methods = ["random","mcts","supervisor"]
action_sequences_above_threshold_all_methods = list()
action_sequences_above_threshold_simulation_only = list()
action_sequences_above_threshold_supervisor_only = list()

for method in search_methods:
    print(method)
    print("\n%%%%%%%%%%%%%%% Evaluate Search Method: "+method+ " %%%%%%%%%%%%%%%\n")

    prefixed = [filename for filename in os.listdir(os.getcwd()+"/results/Scenario_B") if filename.startswith("results_"+method)]
    prefixed.sort()
    print("prefixed:")
    print(prefixed)

    action_sequences_above_threshold_this_method = list()

    risk_threshold = 1
    check_against_supervisor = False

    for file in prefixed:
        print("evaluate file "+file)

        action_sequences = list()
        risks = list()
        parameters = list()

        action_sequences_above_threshold = list()
        risks_above_threshold = list()
        parameters_above_threshold = list()

        results_filepath = os.getcwd()+"/results/Scenario_B/"+file

        assert os.path.exists(results_filepath), "file does not exist!"

        with open(results_filepath) as csvfile:
            reader_obj = csv.reader(csvfile, delimiter=',')
            line_count = 0
            for row in reader_obj:
                if line_count == 0:
                    #print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    risk = float(row[2])
                    action_sequences.append(row[0])
                    parameters.append([row[1]])
                    risks.append(risk)
                    if risk > risk_threshold and (not (row[0] in action_sequences_above_threshold)):
                        action_sequences_above_threshold.append(row[0])
                        risks_above_threshold.append(risk)
                        parameters_above_threshold.append(row[1])
                        line_count += 1

                    if risk > risk_threshold and (not row[0] in action_sequences_above_threshold_this_method):
                        action_sequences_above_threshold_this_method.append(row[0])

                    if row[0][0:12] == "['initial', ":
                        # print("contains initial!")
                        row[0] = row[0].replace("'initial', ","")

                    if (risk > risk_threshold) and (not row[0] in action_sequences_above_threshold_all_methods):
                        action_sequences_above_threshold_all_methods.append(row[0])

                    if (not(method == "supervisor")) and (risk > risk_threshold) and (not row[0] in action_sequences_above_threshold_simulation_only):
                        action_sequences_above_threshold_simulation_only.append(row[0])

                    if (method == "supervisor") and (risk > risk_threshold) and (not row[0] in action_sequences_above_threshold_supervisor_only):
                        action_sequences_above_threshold_supervisor_only.append(row[0])

            # print("number of sequences: "+str(len(action_sequences)))


            print("number of sequences above risk threshold: "+str(len(action_sequences_above_threshold)))
            if risks_above_threshold:
                print("average risk value of hazardous sequences: "+str(sum(risks_above_threshold)/len(risks_above_threshold)))
            if verbose:
                for i in range(len(action_sequences_above_threshold)):
                    print(action_sequences_above_threshold[i] + "; risk: " + str(risks_above_threshold[i])+ "; parameters: " +parameters_above_threshold[i])


            # check_supervisor_inclusion(action_sequences_above_threshold,supervisor_sequences_filepath)

print("action sequences above threshold total: "+str(len(action_sequences_above_threshold_all_methods)))
action_sequences_not_in_supervisor,action_sequences_not_in_simulation = check_supervisor_inclusion(action_sequences_above_threshold_simulation_only,supervisor_sequences_filepath)
print(str(len(action_sequences_above_threshold_all_methods))+" action sequences found by all methods together")
print(str(len(action_sequences_above_threshold_supervisor_only))+" action sequences were found by the formal model.")
print(str(len(action_sequences_not_in_supervisor))+" action sequences were found in simulation but not by the formal model.")
print(str(len(action_sequences_not_in_simulation))+" action sequences were found by the formal model but not in simulation.")

# print(str(len(action_sequences_not_in_supervisor))+" action sequences found in simulation, but not by the formal model")
# print(str(len(action_sequences_not_in_simulation))+" action sequences found by the formal model, but not in simulation.")
# print(str(len(action_sequences_not_in_supervisor))+" action sequences were found in simulation, but not in the formal model.")
# print(str(len(action_sequences_not_in_simulation))+" action sequences were found in the formal model, but not in simulation.")
