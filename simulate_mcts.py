
import b0RemoteApi
import random
import csv
import numpy as np
from Environment import Environment

""" ------------------------ MCTS Implementation ----------------------------"""
""" This part of the code is adapted from: https://ai-boson.github.io/mcts   """

def print_divider():
    print("*******************")

def print_list(input_list):
    output_string = ""
    if input_list:
        for list_element in input_list:
            if type(list_element) == str:
                output_string += " " + list_element
            else:
                output_string += " " + list_element.getAttribute("label")
        print(output_string)
    else:
        print("list empty!")

class MCTSNode():

    def __init__(self, state, state_internal, env, max_episode_length, writer_obj, parent=None, parent_action=None, use_random_parameters = True):
        # print_divider()
        self.env = env # simulation environment
        self.state = state
        self._state_internal = state_internal#this is not the mcts state, only an internal stat variable which is used to determine the currently feasible actions!
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self.max_episode_length = max_episode_length
        self._number_of_visits = 0
        self._cumulative_risk = 0
        self.use_random_parameters = use_random_parameters
        self.writer_obj = writer_obj
        # self._results = defaultdict(int)
        # self._results[1] = 0
        # self._results[-1] = 0
        self._untried_actions = None
        self._untried_actions = self.untried_actions()
        return

    def write_to_csv(self,sequence, params, risk = 0):
        writer.writerow({fieldnames[0]: sequence, fieldnames[1]: params, fieldnames[2]: risk})

    def untried_actions(self):
        # print("get untried action in state: "+self._state_internal.getAttribute("name"))
        self._untried_actions = self.env.workflow_get_feasible_actions(self._state_internal.getAttribute("id"))
        # print_action_list(self._untried_actions)
        return self._untried_actions

    def q(self):
        return self._cumulative_risk

    def n(self):
        return self._number_of_visits

    def expand(self):
        # Select action and update list of untried actions.
        # print("select action from:")
        # print_list(self._untried_actions)
        action = self._untried_actions.pop() # todo: use random action instead of popping first action, but don't forget to remove that action from untried_actio
        print("expand with action " + action.getAttribute("label"))
        # print("action selected:"+action.getAttribute("label"))
        print("run aciton with parameters:" + str(self.env.parameters_current))
        self.env.sim_step(action.getAttribute("label"),self.env.parameters_current)

        """Note: adapt this function. Instead of taking first untried action
        with pop(), select a random action from self._untried_actions"""

        # Get next state (global)
        # if self.state == "":
        #     next_state = self.state + str(action.getAttribute("label"))
        # else:
        next_state = self.state + [str(action.getAttribute("label"))]
        """ Note: The simulation is regarded as black box. Thus, instead of
        using state variales, the state is encoded as string sequence of labels,
        representing the action history."""

        # Update state (internal)
        new_internal_state_index = int(env.workflow_transition(self._state_internal.getAttribute("id"),action))
        next_state_internal = self.env.states[new_internal_state_index]

        #create new node
        child_node = MCTSNode(next_state, next_state_internal, self.env, self.max_episode_length, self.writer_obj, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return len(self.state) >= max_episode_length

    def backpropagate(self, result):
        """ Todo: update risk values according to update rule (TBD)"""
        self._number_of_visits += 1
        self._cumulative_risk += result
        # self._results[result] += 1.
        if self.parent:
             self.parent.backpropagate(result)

    def rollout(self):
        current_rollout_state = self._state_internal
        rollout_episode_counter = len(self.state) # initialize counter with current tree depth, so that overall sequence length remains constant
        rollout_reward = 0
        rollout_actions = list()
        while rollout_episode_counter < self.max_episode_length: # TODO: incorporate max risk threshold as termination criterion!
            # print("rollout from state: "+current_rollout_state.getAttribute("name"))
            possible_moves = self.env.workflow_get_feasible_actions(current_rollout_state.getAttribute("id"))
            action = self.rollout_policy(possible_moves)
            rollout_actions.append(action.getAttribute("label"))
            print("Rollout - choose action: "+action.getAttribute("label"))
            print("run aciton with parameters:" + str(self.env.parameters_current))
            r = self.env.sim_step(action.getAttribute("label"),self.env.parameters_current)
            next_rollout_state_index = int(self.env.workflow_transition(current_rollout_state.getAttribute("id"),action))
            current_rollout_state = self.env.states[next_rollout_state_index]
            rollout_episode_counter += 1
            if r > rollout_reward:
                rollout_reward =  r
        print("reward incurred in this rollout phase: " + str(rollout_reward))
        self.write_to_csv(self.state + rollout_actions, self.env.parameters_current, rollout_reward)
        return rollout_reward

    def rollout_policy(self, possible_moves):
        return random.choice(possible_moves)

    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def best_child(self, c_param=0.1):
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def _tree_policy(self):
        current_node = self
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
                action = self.env.workflow_get_event_by_label(current_node.state[-1])
                print("traverse to node: " + str(current_node.state) + "with action " + action.getAttribute("label"))
                print("run aciton with parameters:" + str(self.env.parameters_current))
                self.env.sim_step(action.getAttribute("label"),self.env.parameters_current)
        return current_node

    def best_action(self):
        """ Todo: reset simulation after each episode! """
        simulation_no = 10
        for i in range(simulation_no):
            print_divider()
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
            self.env.sim_reset()
            self.env.sim_randomize_parameters()
            print("RESET")
        return self.best_child(c_param=0)


"""--------------------------------------------------------------------------"""

max_episode_length = 9
sim_params_min = [-0.2, 0.8, 1]
sim_params_max = [0.2, 1.2, 1.5]
sim_params_nominal = [0,1,1]
workflow_xml_path = "models/supremica/XML/human_model_scenario_A.xml"

with b0RemoteApi.RemoteApiClient('b0RemoteApi_V-REP-addOn','b0RemoteApiAddOn') as client:  #This line defines the client, which provides all functions of the remote API
    env = Environment(client,sim_params_min,sim_params_max,sim_params_nominal,workflow_xml_path,False)
    env.sim_start()
    results_filepath = "results/results_mcts_scenario_A.csv"
    # with open(results_filepath, 'w', newline='') as csvfile:
    #     # fieldnames = ['sequence']
    #     writer = csv.writer(csvfile)#, fieldnames=fieldnames)
    with open(results_filepath, 'w', newline='') as csvfile:
        fieldnames = ['sequence', 'param', 'risk']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        initial_node = MCTSNode(["initial"],env.states[0],env,max_episode_length,writer)
        initial_node.best_action()
        env.sim_stop()

    # next_node = initial_node.expand()
    #
    # next_node.expand()
    #
    # print_divider()
    #
    # print_list(initial_node.state)
    # print("child nodes:")
    # for child_node in initial_node.children:
    #     print_list(child_node.state)
    #
    # print_divider()
    #
    # print_list(next_node.state)
    # print("child nodes:")
    # for child_node in next_node.children:
    #     print_list(child_node.state)
    #     print(child_node.is_terminal_node())
    #
    # print("parent:")
    # print_list(child_node.parent.state)
    #
    #
    # res = child_node.rollout()
    # child_node.backpropagate(res)
    #
    # child_node_2 = initial_node.expand()
    # res = child_node_2.rollout()
    # child_node_2.backpropagate(res)
    #
    # print_divider()
    # print_list(initial_node.state)
    # print("n: "+str(initial_node.n()))
    # print("q: "+str(initial_node.q()))
    # for child in initial_node.children:
    #     print_list(child.state)
    #     print("n: "+str(child.n()))
    #     print("q: "+str(child.q()))
    # print("best child")
    # print(initial_node.best_child().state)

# class State():
#
#     def __init__(self,sim_client,sim_params_min,sim_params_max,sim_params_nominal,workflow_xml_path,max_sequence_length):
#         self.env = Environment(sim_client,sim_params_min,sim_params_max,sim_params_nominal,workflow_xml_path)
#         print("initialize")
#         self.max_sequence_length = max_sequence_length
#         self.initial_state = self.env.states[0]
#         self.current_state = self.initial_state
#         self.action_counter = 0
#         self.current_action_sequence = list()
# #
#     def get_legal_actions(self):
#         return env.workflow_get_feasible_actions(self._state_internal.getAttribute("id"))
#
#     def takeAction(self, action):
#         print("take action")
#         current_state_id = self.current_state.getAttribute("id")
#         next_state_id = int(self.env.workflow_transition(current_state_id,action))
#         self.current_state = self.env.states[next_state_id]
#         self.current_action_sequence.append(action)
#         self.action_counter += 1
#         return self.current_state
#
#     def isTerminal(self):
#         print("terminate")
#         # return (len(self.current_action_sequence) >= self.max_sequence_length) #or risk > threshold
#         return self.action_counter >= self.max_sequence_length
#
#     def getReward(self):
#         return random.random()

# """ -------------------------- main script ----------------------------------"""
#
# ########################## Simulation Settings #################################
# scenario = 1 # Currently available: {1,2}
# use_random_parameters = False
# n_simulation_runs = 960
# log_results = True
# max_episode_length = 9
#
# ####################### Load scenario parameters ###############################
# if scenario == 1:
#     motionParametersMin = [-0.2,0.8, 1]
#     motionParametersMax = [0.2, 1.2, 1.5]
#     motionParametersNominal = [0,1,1]
#     automaton_filepath = "models/supremica/XML/human_model_scenario_A.xml"
#     action_sequence_filepath="models/supremica/CSV/action_sequences_human_model_scenario_A.csv"
#     results_filepath = "results/results_random_scenario_A.csv"
# else:
#     "Error! Select valid scenario number (1) in line 9!"
# with b0RemoteApi.RemoteApiClient('b0RemoteApi_V-REP-addOn','b0RemoteApiAddOn') as client:  #This line defines the client, which provides all functions of the remote API
#     # create and initialize simution environment
#
#     state = State(client,motionParametersMin,motionParametersMax,motionParametersNominal,automaton_filepath,max_episode_length)
#
#     #o random episodes (for testing only)
#     while not state.isTerminal():
#         possible_actions = state.getPossibleActions()
#         random_action = random.choice(possible_actions)
#         print(random_action.getAttribute("label") + " leads from state " + state.current_state.getAttribute("name")+"...")
#         state.takeAction(random_action)
#         print("...to state " + state.current_state.getAttribute("name"))
#         print("reward: " + str(state.getReward()))
