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

results_filepath = os.getcwd()+"/results/results_random_scenario_B.csv"
#esults_filepath = os.getcwd()+"/results/Archive/results_random_scenario_B_04.csv"

action_sequences = list()
risks = list()
parameters = list()

action_sequences_above_threshold = list()
risks_above_threshold = list()
parameters_above_threshold = list()

risk_threshold = 1

if os.path.exists(results_filepath):
    print("exist")
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
                print(risk)
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
# print(actionSequences)
