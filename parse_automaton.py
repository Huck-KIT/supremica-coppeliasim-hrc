import os
import time
import csv
from xml.dom.minidom import parse, Node

#settings
max_sequence_length = 10
save_results = True
terminate_on_event = True
filepath_source = "models/supremica/XML/supervisor_scenario_B.xml"
filepath_dest = "models/supremica/CSV/action_sequences_supervisor_scenario_B.csv"

# initializations
language_subset = list()
action_space = list()
initialState = None

# functions
def get_feasible_events(state_id):
    # get all events that have the state id as source
    feasible_events = list()
    for transition in transitions:
        if event.getAttribute("source") == state_id:
            feasible_events.append(event)
    return feasible_events

def print_sequence(input_sequence):
    output_string = ""
    for event in input_sequence:
        output_string += event.getAttribute("label")+" "
    print(output_string)

def transition(current_state_id,event):
    for transition in transitions:
        if transition.getAttribute("source") == current_state_id and transition.getAttribute("event") == event.getAttribute("id"):
            # print("Event "+event.getAttribute("label")+" in state "+current_state_id+" leads to state "+transition.getAttribute("dest"))
            return transition.getAttribute("dest")
    # print("Event "+event.getAttribute("label")+" not feasible in state "+current_state_id)
    return None

def check_automaton_acceptance(input_state_id,input_sequence):
    if input_sequence == []:
        return True,input_state_id
    else:
        next_state_id = transition(input_state_id,input_sequence[-1])
        if next_state_id == None:
            return False, input_state_id
        else:
            return True, next_state_id

    ############### old version ######################

    # print("cehck sequence: ")
    # print_sequence(input_sequence)
    # current_state_id = initial_state.getAttribute("id")
    # # print("\n-------check new sequence--------")
    # for event in input_sequence:
    #     current_state_id = transition(current_state_id,event)
    #     if current_state_id == None:
    #         return False, None
    # return True, None

def sequence_is_terminal(input_sequence):
    if input_sequence == None:
        return False
    else:
        return len(input_sequence) >= max_sequence_length or terminal_event in input_sequence

def calculate_language_subset(input_state_id,input_sequence):
    # Sequence is not accepted --> return without adding the sequence to the set
    success, next_state_id = check_automaton_acceptance(input_state_id,input_sequence)
    if not success:
        print("A")
        # print("Sequence is not accepted")
        return None
    # Sequence is accepted, but reaches terminal length without including a collision --> return without adding the sequence to the set
    elif terminate_on_event and len(input_sequence) >= max_sequence_length and not (terminal_event in input_sequence):
        print("B")
        # print_sequence(input_sequence)
        # print("Sequence is accepted but reaches terminal length without including a collision")
        return None
    # Sequence is accepted and includes terminal event --> add sequence to set
    elif terminate_on_event and (terminal_event in input_sequence):
        print("C")
        # print_sequence(input_sequence)
        # print("Sequence is accepted and includes terminal event --> add sequence to set")
        input_sequence_labels = list()
        for input in input_sequence:
            input_sequence_labels.append(input.getAttribute("label"))
        language_subset.append(input_sequence_labels)
        return None
    elif not terminate_on_event and len(input_sequence) == max_sequence_length:
        print("D")
        # print_sequence(input_sequence)
        # print("Sequence is accepted and includes terminal event --> add sequence to set")
        input_sequence_labels = list()
        for input in input_sequence:
            input_sequence_labels.append(input.getAttribute("label"))
        language_subset.append(input_sequence_labels)
        return None
    else:
        for event in events:
            temp_sequence = input_sequence+[event]
            calculate_language_subset(next_state_id,temp_sequence)

###############################################################################

# def transition(input_event):
#     global current_state
#     print("check event: "+input_event.getAttribute("label")+"("+input_event.getAttribute("id")+") in state "+str(current_state))
#     for transition in transitions:
#         if transition.getAttribute("source") == current_state and transition.getAttribute("event") == input_event.getAttribute("id"):
#             # print("Event "+event.getAttribute("label")+" in state "+current_state_id+" leads to state "+transition.getAttribute("dest"))
#             return transition.getAttribute("dest")
#     # print("Event "+event.getAttribute("label")+" not feasible in state "+current_state_id)
#     return None
#
# def print_current_sequence():
#     global current_sequence
#     for seq_event in current_sequence:
#         print(seq_event.getAttribute("label"))

# def get_feasible_events():
#
#     # get all events that have the state id as source
#     feasible_events = list()
#     for transition in transitions:
#         if transition.getAttribute("source") == current_state:
#             feasible_events.append(events[int(transition.getAttribute("event"))])
#     return feasible_events

# def check_terminal(input_sequence):
#     if len(input_sequence) >= max_sequence_length:
#         length_exceeded = True
#     else:
#         length_exceeded = False
#     if terminal_event in input_sequence:
#         print("terminal event included!")
#         terminal_event_included = True
#     else:
#         terminal_event_included = False
#     return (length_exceeded or terminal_event_included), (length_exceeded and terminal_event_included)

# def check_event(input_event):
#     global current_state,current_sequence,level_counter
#     print("level: "+str(level_counter))
#     level_counter += 1
#     print("current state: "+current_state)
#     print("current sequence:")
#     #print_current_sequence()
#     print(current_sequence)
#     next_state = transition(input_event)
#     if next_state == None:
#         print("event not feasible")
#         #current_state = initial_state
#         #current_sequence.clear()
#         return 0
#     else:
#         current_state = next_state
#         print("event leads to state "+str(current_state))
#         current_sequence.append(input_event.getAttribute("label"))
#         is_terminal, is_accepted = check_terminal(current_sequence)
#         if is_terminal:
#             print("sequence is terminal")
#             if is_accepted:
#                 print("sequence is accepted")
#                 set_of_sequences.append(current_sequence)
#             current_state = initial_state
#             current_sequence.clear()
#             return 0
#         else:
#             print("sequence not terminal, check further")
#             for next_event in events:
#                 check_event(next_event)




start_time = time.time()

# main script
with open(filepath_source) as file:
    document = parse(file)

    # parse xml
    events      = document.getElementsByTagName("Event")
    states      = document.getElementsByTagName("State")
    transitions = document.getElementsByTagName("Transition")

    initial_state   = states[0]
    if terminate_on_event:
        terminal_event  = events[0] #None for human model
    else:
        terminal_event = None

    current_state_id_global = "0"
    current_sequence = list()
    set_of_sequences = list()
    action_sequence = list()
    level_counter = 0
    calculate_language_subset("0",action_sequence)

    # for event in events:
    #     check_event(event)

    for sequence in language_subset:
        print(sequence)

    print(str(len(language_subset))+" action sequences found:")
print("--- %s seconds ---" % (time.time() - start_time))

if save_results:
    with open(filepath_dest, 'w') as csvfile:
        writer_obj = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for seq in language_subset:
            writer_obj.writerow(seq)
