"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
simulate_mcts.py

Author: Tom P. Huck
Karlsruhe Institute of Technology (KIT), Karlsruhe, Germany
Date: 2022-07-15

This script explores action sequences in the simulator using monte carlo tree
search. The automaton xml file (see 'workflow_xml_path'), which is generated
from supremica, determines what action sequences are feasible.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

import b0RemoteApi
import random
import csv
import numpy as np
from Environment import Environment

""" ------------------------ MCTS Implementation ----------------------------"""

""" Source acknowledgment:
This section of the code was adapted from: https://ai-boson.github.io/mcts
"""

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
        self._untried_actions = None
        self._untried_actions = self.untried_actions()
        return

    def write_to_csv(self,sequence, params, risk = 0):
        writer.writerow({fieldnames[0]: sequence, fieldnames[1]: params, fieldnames[2]: risk})

    def untried_actions(self):
        self._untried_actions = self.env.workflow_get_feasible_actions(self._state_internal.getAttribute("id"))
        return self._untried_actions

    def q(self):
        return self._cumulative_risk

    def n(self):
        return self._number_of_visits

    def expand(self):
        # Select action and update list of untried actions.
        action = self._untried_actions.pop() # todo: use random action instead of popping first action, but don't forget to remove that action from untried_actio
        print("expand with action " + action.getAttribute("label"))
        # print("action selected:"+action.getAttribute("label"))
        print("run aciton with parameters:" + str(self.env.parameters_current))
        self.env.sim_step(action.getAttribute("label"),self.env.parameters_current)

        """Todo: adapt this function. Instead of taking first untried action
        with pop(), select a random action from self._untried_actions"""

        # Get next state (global)
        next_state = self.state + [str(action.getAttribute("label"))]
        """ Note: The simulation is regarded as black box. Thus, instead of
        using state variales, the state is encoded as string sequence of labels,
        representing the action history."""

        # Update state (internal)
        new_internal_state_index = int(env.workflow_transition(self._state_internal.getAttribute("id"),action))
        next_state_internal = self.env.states[new_internal_state_index]
        """ Note: This state is not used in the mcts search. It is only
        maintained to determine what actions are currently feasible"""

        #create new node
        child_node = MCTSNode(next_state, next_state_internal, self.env, self.max_episode_length, self.writer_obj, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return len(self.state) >= max_episode_length

    def backpropagate(self, result):
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
                self.env.sim_step(action.getAttribute("label"),self.env.parameters_current)

        return current_node

    def search(self):
        simulation_no = 500

        for i in range(simulation_no):
            print_divider()
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
            self.env.sim_reset()
            self.env.sim_randomize_parameters()
            print("RESET")

        return self.best_child(c_param=0)


"""--------------------------------- Main -----------------------------------"""

max_episode_length = 9
scenario = 1

if scenario == 1:
    sim_params_min = [-0.2, 0.8, 1]
    sim_params_max = [0.2, 1.2, 1.5]
    sim_params_nominal = [0,1,1]
    workflow_xml_path = "models/supremica/XML/human_model_scenario_A.xml" # automaton xml file (created from supremica)
    results_filepath = "results/results_mcts_scenario_A.csv" # log file
else:
    print("error - enter valid scenario (must be 1 or 2)")

 #This line defines the simulation client, which provides all functions of the remote API
with b0RemoteApi.RemoteApiClient('b0RemoteApi_V-REP-addOn','b0RemoteApiAddOn') as client:

     #Client is passed to the environment object, which encapsulates all the simulator functionalities
    env = Environment(client,sim_params_min,sim_params_max,sim_params_nominal,workflow_xml_path,False)
    env.sim_start()

    with open(results_filepath, 'w', newline='') as csvfile:
        fieldnames = ['sequence', 'param', 'risk']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        # Environment object is passed to the initial mcts node, so that mcts can access the simulation functionalities
        initial_node = MCTSNode(["initial"],env.states[0],env,max_episode_length,writer)
        initial_node.search() # trigger mcts
        env.sim_stop()
