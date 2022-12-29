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

def get_supervisor_sequences(supervisor_sequences_filepath):
    action_sequences_supervisor = list()
    with open(supervisor_sequences_filepath) as supervisor_csvfile:
        reader_obj = csv.reader(supervisor_csvfile, delimiter=',')
        for row in reader_obj:
            sequence = row[0]
            sequence = sequence.replace(" collision","")
            action_sequences_supervisor.append(sequence)
    return action_sequences_supervisor

def convert_to_string(list_of_lists):
# converts list of lists to list of strings
    list_of_strings = list()
    for element in list_of_lists:
        if element[0] == 'initial':
            del element[0]
        list_as_string = str(element)
        list_as_string = remove_separators_from_string(list_as_string)
        list_of_strings.append(list_as_string)
    return list_of_strings

def intersection_of_lists(list1,list2):
    set1 = set(list1)
    set2 = set(list2)
    return list(set1.intersection(set2))

def substraction_of_lists(list1,list2):
    set1 = set(list1)
    set2 = set(list2)
    return list(set1-set2)

# def check_supervisor_inclusion(simulation_action_sequences,supervisor_sequences_filepath):
#     """ this function compares if the action sequences given by the list
#     action_sequences are included in the action sequences obtained from the
#     supervisor (given by the file at supervisor_file_path)"""
#
#     #read in action sequences
#     action_sequences_supervisor = list()
#     with open(supervisor_sequences_filepath) as supervisor_csvfile:
#         reader_obj = csv.reader(supervisor_csvfile, delimiter=',')
#         for row in reader_obj:
#             sequence_as_list = list()
#             action_sequences_supervisor.append(row)
#
#     # compare
#     sequences_not_in_supervisor = list() # action sequences in simulation, but not in supervisor
#     for input_sequence in simulation_action_sequences:
#         # convert list into string for comparison
#         input_sequence_as_list = input_sequence.split()
#         if input_sequence_as_list[0] == "['initial',":
#             del input_sequence_as_list[0] #remove 'initial' tag
#         input_sequence_as_string = str(input_sequence_as_list)
#         input_sequence_as_string = remove_separators_from_string(input_sequence_as_string)
#
#         #compare with supervisor sequences
#         supervisor_sequences_as_string = list()
#         for supervisor_sequence in action_sequences_supervisor:
#             supervisor_sequence_as_string = supervisor_sequence[0]#.remove('collision') # remove "collision" tag
#             supervisor_sequence_as_list = supervisor_sequence_as_string.split()
#             supervisor_sequence_as_list.remove("collision")
#             supervisor_sequence_as_string = str(supervisor_sequence_as_list)
#             supervisor_sequence_as_string = remove_separators_from_string(supervisor_sequence_as_string)
#             supervisor_sequences_as_string.append(supervisor_sequence_as_string)
#
#         if not (input_sequence_as_string in supervisor_sequences_as_string):
#             sequences_not_in_supervisor.append(input_sequence_as_string)
#
#     sequences_not_in_simulation = list() # action sequences in supervisor, but not in simulation
#     for supervisor_sequence in action_sequences_supervisor:
#         # print("compare: ")
#         comp_string1 = supervisor_sequence[0].replace(" collision","")
#         comp_string_list = list()
#         for seq in simulation_action_sequences:
#             comp_string2 = remove_separators_from_string(seq)
#             if "initial " in comp_string2:
#                 comp_string2.replace("initial ","")
#             comp_string_list.append(comp_string2)
#         print("compare:")
#         print(comp_string1)
#         print("with:")
#         print(comp_string_list)
#         if comp_string1 in comp_string_list:
#             print("included!")
#         else:
#             print("not included")
#             sequences_not_in_simulation.append(supervisor_sequence)
#             # print("seq not in simulation: "+str(len(sequences_not_in_simulation)))
#     print(str(len(sequences_not_in_simulation))+" sequences not in simulation")
#     return sequences_not_in_supervisor,sequences_not_in_simulation

scenario =  "F"

supervisor_sequences_filepath = os.getcwd()+"/models/supremica/CSV/action_sequences_supervisor_scenario_"+scenario+".csv"
#esults_filepath = os.getcwd()+"/results/Archive/results_random_scenario_B_04.csv"

search_methods = ["random","mcts","supervisor"]
action_sequences_above_threshold_all_methods = list()
action_sequences_above_threshold_simulation_only = list()
action_sequences_above_threshold_supervisor_only = list()

for method in search_methods:
    print(method)
    print("\n%%%%%%%%%%%%%%% Evaluate Search Method: "+method+ " %%%%%%%%%%%%%%%\n")

    prefixed = [filename for filename in os.listdir(os.getcwd()+"/results/Scenario_"+scenario) if filename.startswith("results_"+method)]
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

        results_filepath = os.getcwd()+"/results/Scenario_"+scenario+"/"+file

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


# print("action sequences above threshold total: "+str(len(action_sequences_above_threshold_all_methods)))
# action_sequences_not_in_supervisor,action_sequences_not_in_simulation = check_supervisor_inclusion(action_sequences_above_threshold_all_methods,supervisor_sequences_filepath)
# print(str(len(action_sequences_above_threshold_all_methods))+" action sequences found by all methods together")
# print(str(len(action_sequences_above_threshold_supervisor_only))+" action sequences were found by the formal model.")
# print(str(len(action_sequences_not_in_supervisor))+" action sequences were found in simulation but not by the formal model.")
# print(str(len(action_sequences_not_in_simulation))+" action sequences were found by the formal model but not in simulation.")

print("supervisor action sequences: ")
sup_list = get_supervisor_sequences(supervisor_sequences_filepath)
sup_list.sort()
print(sup_list)
print(len(sup_list))

print("simulation action sequences: ")
sim_list = convert_to_string(action_sequences_above_threshold_all_methods)
sim_list.sort()
print(sim_list)
print(len(sim_list))

print("sequences contained in supervisor and confirmed by simulation (true positives of the supervisor): ")
sim_intersect_sup = intersection_of_lists(sup_list,sim_list)
print(sim_intersect_sup)
print(len(sim_intersect_sup))

print("sequences contained in supervisor, but NOT confirmed in simulation (false positives of the supervisor): ")
sup_minus_sim = substraction_of_lists(sup_list,sim_list)
print(sup_minus_sim)
print(len(sup_minus_sim))

print("sequences NOT contained in supervisor, but identified as hazardous in simulation (false negatives of the supervisor): ")
sim_minus_sup = substraction_of_lists(sim_list,sup_list)
print(sim_minus_sup)
print(len(sim_minus_sup))
