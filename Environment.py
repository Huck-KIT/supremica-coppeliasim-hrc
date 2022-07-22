"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Environment.py

Author: Tom P. Huck
Karlsruhe Institute of Technology (KIT), Karlsruhe, Germany
Date: 2022-07-08

This module defines the Environment class, which encapsulates all
functionalities of the simulator and the automaton.

Automaton:
- Get list of feasible actions in given state
- Get next state for given state and action
- Check if sequence of events is accepted by the automaton

Simulator:
- Start simulations
- Perform actions in simulation and retrieve risk metric
- Reset simulation state
- Stop simulation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

import csv
import random
from xml.dom.minidom import parse, Node

class Environment:
    def __init__(self,sim_client,sim_params_min,sim_params_max,sim_params_nominal,workflow_xml_path,manual_trigger):
        # assign constructor inputs
        self.client = sim_client
        self.sim_params_max = sim_params_max
        self.sim_params_min = sim_params_min
        self.sim_params_nominal = sim_params_nominal
        self.step_counter = 0
        self.current_max_risk = 0 # tracks risk value of ongoing simulation
        self.manual_trigger = manual_trigger
        self.parameters_current = sim_params_nominal

        with open(workflow_xml_path) as file:
            document = parse(file)
            self.events      = document.getElementsByTagName("Event")
            self.states      = document.getElementsByTagName("State")
            self.transitions = document.getElementsByTagName("Transition")

        self.action_space = list()
        for event in self.events:
            self.action_space.append(event.getAttribute("label"))
        self.initial_state   = self.states[0]
        self.terminal_event  = self.events[0]

    """ ---------------------- Automaton functions --------------------------"""

    def workflow_get_event_by_label(self,event_label):
        for event in self.events:
            if event.getAttribute("label") == event_label:
                return event
        return None

    def workflow_transition(self,current_state_id,event):
        for transition in self.transitions:
            if transition.getAttribute("source") == current_state_id and transition.getAttribute("event") == event.getAttribute("id"):
                # print("Event "+event.getAttribute("label")+" in state "+current_state_id+" leads to state "+transition.getAttribute("dest"))
                return transition.getAttribute("dest")
        # print("Event "+event.getAttribute("label")+" not feasible in state "+current_state_id)
        return None

    def workflow_get_feasible_actions(self, current_state_id):
        feasible_actions = list()
        for transition in self.transitions:
            if transition.getAttribute("source") == current_state_id:
                action = self.events[int(transition.getAttribute("event"))] #attribute id is saved as string --> cast to int
                if not (action in feasible_actions):
                    feasible_actions.append(action)
        return feasible_actions

    def workflow_check_acceptance(self, input_sequence):
        current_state_id = self.initial_state.getAttribute("id")
        # print("\n-------check new sequence--------")
        for event in input_sequence:
            assert event in self.events or event in self.action_space, "Unknown event in sequence!"
            if event in self.events:
                current_state_id = self.workflow_transition(current_state_id,event)
                if current_state_id == None:
                    return False
            elif event in self.action_space:
                current_state_id = self.workflow_transition(current_state_id,self.workflow_get_event_by_label(event))
                if current_state_id == None:
                    return False
        return True


    """ ---------------------- Simulator functions --------------------------"""

    def sim_start(self):
        self.client.simxSynchronous(True)
        self.client.simxStartSimulation(self.client.simxServiceCall())

    def sim_set_parameters(self,parameters):
        assert len(parameters) == len(self.sim_params_min), "too many/few parameters"
        assert len(parameters) == len(self.sim_params_max), "too many/few parameters"
        for i in range(len(parameters)):
            assert parameters[i] <= self.sim_params_max and parameters[i] >= self.sim_params_min[i], "parameter "+str(i)+"out fo bounds"
        self.parameters_current = parameters
        """ TODO: call script function to set parameters """

    def sim_randomize_parameters(self):
        current_parameters = list() # use default parameters
        for i in range(3):
            current_parameters.append(self.sim_params_min[i]+(self.sim_params_max[i]-self.sim_params_min[i])*random.random())
        self.parameters_current = current_parameters

    def sim_reset(self):
        print("--------- reset simulation ---------")
        self.client.simxCallScriptFunction("reset@Bill","sim.scripttype_childscript",1,self.client.simxServiceCall())
        self.step_counter = 0
        self.current_max_risk = 0

    def sim_step(self,action,parameters):
        if self.manual_trigger:
            print("press enter to continue")
            input()
        self.step_counter +=1
        current_max_risk_action = 0 # current max risk incurred in this action
        assert action in self.action_space, "Action not in action space!"

        action_is_set = False
        while not action_is_set:
            action_is_set,_ = self.client.simxCallScriptFunction("setAction@Bill","sim.scripttype_childscript",action,self.client.simxServiceCall())
            self.client.simxCallScriptFunction("setMotionParameters@Bill","sim.scripttype_childscript",parameters,self.client.simxServiceCall())
            self.client.simxSynchronousTrigger()

        action_is_running = True
        while action_is_running:
            self.client.simxSynchronousTrigger()
            _,action_is_running = self.client.simxCallScriptFunction("isHumanModelActive@Bill","sim.scripttype_childscript",1,self.client.simxServiceCall())
            _,risk = self.client.simxCallScriptFunction("getMaxRisk@RiskMetricCalculator","sim.scripttype_childscript",1,self.client.simxServiceCall())
            if risk > current_max_risk_action:
                current_max_risk_action =  risk

        isReset = self.client.simxCallScriptFunction("resetMaxRisk@RiskMetricCalculator","sim.scripttype_childscript",1,self.client.simxServiceCall())
        assert isReset, "error - could not reset risk metric after action"
        print("risk incurred in this action: "+str(current_max_risk_action))
        if current_max_risk_action > self.current_max_risk:
            self.current_max_risk = current_max_risk_action # update overall max risk
        return current_max_risk_action

    def get_max_risk(self):
        return self.current_max_risk

    def get_step_number(self):
        return self.step_counter

    def sim_stop(self):
        self.client.simxStopSimulation(self.client.simxServiceCall())

    def print_action_space(self):
        print("action space:")
        for action in self.action_space:
            print(action)
