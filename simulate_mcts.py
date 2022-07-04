""" -------------------------- wrapper class --------------------------------"""

""" This wrapper wraws the Environment class for use with the python mcts package
(see https://pypi.org/project/mcts/) by providing the following functions:
- getPossibleActions(): Returns an iterable of all actions which can be taken from this state
- takeAction(action): Returns the state which results from taking action action
- isTerminal(): Returns whether this state is a terminal state
- getReward(): Returns the reward for this state. Only needed for terminal states.
"""
import b0RemoteApi
import random
from Environment import Environment

class State():

    def __init__(self,sim_client,sim_params_min,sim_params_max,sim_params_nominal,workflow_xml_path,max_sequence_length):
        self.env = Environment(sim_client,sim_params_min,sim_params_max,sim_params_nominal,workflow_xml_path)
        print("initialize")
        self.max_sequence_length = max_sequence_length
        self.initial_state = self.env.states[0]
        self.current_state = self.initial_state
        self.action_counter = 0
        self.current_action_sequence = list()

    def getPossibleActions(self):
        return self.env.workflow_get_feasible_actions(self.current_state.getAttribute("id"))

    def takeAction(self, action):
        print("take action")
        current_state_id = self.current_state.getAttribute("id")
        next_state_id = int(self.env.workflow_transition(current_state_id,action))
        self.current_state = self.env.states[next_state_id]
        self.current_action_sequence.append(action)
        self.action_counter += 1
        return self.current_state

    def isTerminal(self):
        print("terminate")
        # return (len(self.current_action_sequence) >= self.max_sequence_length) #or risk > threshold
        return self.action_counter >= self.max_sequence_length

    def getReward(self):
        return random.random()

""" -------------------------- main script ----------------------------------"""

########################## Simulation Settings #################################
scenario = 1 # Currently available: {1,2}
use_random_parameters = False
n_simulation_runs = 960
log_results = True
max_episode_length = 9

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
with b0RemoteApi.RemoteApiClient('b0RemoteApi_V-REP-addOn','b0RemoteApiAddOn') as client:  #This line defines the client, which provides all functions of the remote API
    # create and initialize simution environment

    state = State(client,motionParametersMin,motionParametersMax,motionParametersNominal,automaton_filepath,max_episode_length)

    #o random episodes (for testing only)
    while not state.isTerminal():
        possible_actions = state.getPossibleActions()
        random_action = random.choice(possible_actions)
        print(random_action.getAttribute("label") + " leads from state " + state.current_state.getAttribute("name")+"...")
        state.takeAction(random_action)
        print("...to state " + state.current_state.getAttribute("name"))
        print("reward: " + str(state.getReward()))
