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

def remove_separators_from_string(input_string):
        input_string = input_string.replace(",","")
        input_string = input_string.replace("'","")
        input_string = input_string.replace("\"","")
        input_string = input_string.replace("[","")
        input_string = input_string.replace("]","")
        return input_string

def check_supervisor_inclusion(input_action_sequences,supervisor_sequences_filepath):
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
    sequences_not_in_supervisor = list()
    for input_sequence in input_action_sequences:
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
    if sequences_not_in_supervisor:
        print(str(len(sequences_not_in_supervisor))+" sequences not covered by supervisor:")
        for seq in sequences_not_in_supervisor:
            print(seq)
    else:
        print("all sequences covered in supervisor")



results_filepath = os.getcwd()+"/results/results_supervisor_scenario_A.csv"
supervisor_sequences_filepath = os.getcwd()+"/models/supremica/CSV/action_sequences_supervisor_scenario_A.csv"
#esults_filepath = os.getcwd()+"/results/Archive/results_random_scenario_B_04.csv"

action_sequences = list()
risks = list()
parameters = list()

action_sequences_above_threshold = list()
risks_above_threshold = list()
parameters_above_threshold = list()

risk_threshold = 1

check_against_supervisor = False

assert os.path.exists(results_filepath), "file does not exist!"

    #riskValues = np.loadtxt(filepath+"/risks.csv", delimiter=',')
    # reader_oi = pd.read_csv(filepath+"/actionSequences.csv", delimiter=',', names=list(range(10)))
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

    print("number of sequences: "+str(len(action_sequences)))


    print("number of sequences above risk threshold: "+str(len(action_sequences_above_threshold)))
    for i in range(len(action_sequences_above_threshold)):
        print(action_sequences_above_threshold[i] + "; risk: " + str(risks_above_threshold[i])+ "; parameters: " +parameters_above_threshold[i])


    check_supervisor_inclusion(action_sequences_above_threshold,supervisor_sequences_filepath)
    # if check_against_supervisor:
    #     sim_params_min = [0.7, -0.1, -0.1]
    #     sim_params_max = [1.3, 0, 0.1]
    #     sim_params_nominal = [1, 0, 0]
    #     workflow_xml_path = "models/supremica/XML/supervisor_scenario_B.xml"
    #     env = Environment(None,sim_params_min,sim_params_max,sim_params_nominal,workflow_xml_path,False)
    #     action_sequences_non_supervised = list()
    #     for sequence_string in action_sequences_above_threshold:
    #         sequence_string = sequence_string.replace(",","")
    #         sequence_string = sequence_string.replace("'","")
    #         sequence_string = sequence_string.replace("[","")
    #         sequence_string = sequence_string.replace("]","")
    #         sequence_list = sequence_string.split()
    #         if "initial" in sequence_list:
    #             sequence_list.remove("initial")
    #         print(sequence_list)
    #         print(env.workflow_check_acceptance(sequence_list))
    #         if not env.workflow_check_acceptance(sequence_list):
    #             action_sequences_non_supervised.append(sequence_list)
    #     print("Action sequences NOT accepted by supervisor:")
    #     if action_sequences_non_supervised:
    #         print(action_sequences_non_supervised)
    #     else:
    #         print("NONE.")
