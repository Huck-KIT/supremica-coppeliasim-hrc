import csv
from xml.dom.minidom import parse, Node

class Environment:
    def __init__(self,sim_client,sim_params_min,sim_params_max,sim_params_nominal,workflow_xml_path):
        # assign constructor inputs
        self.client = sim_client
        self.sim_params_max = sim_params_max
        self.sim_params_min = sim_params_min
        self.sim_params_nominal = sim_params_nominal

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

    def sim_start(self):
        self.client.simxSynchronous(True)
        self.client.simxStartSimulation(self.client.simxServiceCall())

    def sim_set_parameters(self,parameters):
        assert len(parameters) == len(self.sim_params_min), "too many/few parameters"
        assert len(parameters) == len(self.sim_params_max), "too many/few parameters"
        for i in range(len(parameters)):
            assert parameters[i] <= self.sim_params_max and parameters[i] >= self.sim_params_min[i], "parameter "+str(i)+"out fo bounds"
        """ TODO: call script function to set parameters """

    def sim_reset(self):
        print("--------- reset simulation ---------")
        self.client.simxCallScriptFunction("reset@Bill","sim.scripttype_childscript",1,self.client.simxServiceCall())

    def sim_step(self,action,parameters):
        current_max_risk = 0
        assert action in self.action_space, "Action not in action space!"
        action_is_set = False
        while not action_is_set:
            action_is_set,_ = self.client.simxCallScriptFunction("setAction@Bill","sim.scripttype_childscript",action,self.client.simxServiceCall())
            self.client.simxSynchronousTrigger()
        action_is_running = True
        while action_is_running:
            self.client.simxSynchronousTrigger()
            _,action_is_running = self.client.simxCallScriptFunction("isHumanModelActive@Bill","sim.scripttype_childscript",1,self.client.simxServiceCall())
            _,risk = self.client.simxCallScriptFunction("getMaxRisk@RiskMetricCalculator","sim.scripttype_childscript",1,self.client.simxServiceCall())
            if risk > current_max_risk:
                current_max_risk =  risk
        isReset = self.client.simxCallScriptFunction("resetMaxRisk@RiskMetricCalculator","sim.scripttype_childscript",1,self.client.simxServiceCall())
        assert isReset, "error - could not reset risk metric after action"
        return current_max_risk


    def sim_stop(self):
        self.client.simxStopSimulation(self.client.simxServiceCall())

    def print_action_space(self):
        print("action space:")
        for action in self.action_space:
            print(action)
