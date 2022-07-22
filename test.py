from Environment import Environment
import b0RemoteApi


sim_params_min = [0.7, -0.1, -0.1]
sim_params_max = [1.5, 0, 0.1]
sim_params_nominal = [1, 0, 0]
workflow_xml_path = "models/supremica/XML/human_model_scenario_B.xml"

parameters = [1.5, -0.05, 0] #walkingvel, reaching offset x, reaching offset y
# action_sequence = [ 'human_press_button_1', 'human_retract_hand', 'human_transition_1',
#                     'human_pick_up_part_storage', 'human_retract_hand', 'human_transition_1',
#                     'human_transition_2', 'human_put_down_part_robot', 'human_pick_up_part_robot', 'human_retract_hand']

action_sequence = [ 'human_transition_1', 'human_pick_up_part_storage', 'human_retract_hand',
                    'human_transition_1', 'human_transition_2', 'human_put_down_part_robot',
                    'human_retract_hand', 'human_transition_2', 'human_press_button_1',
                    'human_retract_hand', 'human_transition_2','human_pick_up_part_robot']

with b0RemoteApi.RemoteApiClient('b0RemoteApi_V-REP-addOn','b0RemoteApiAddOn') as client:

     #Client is passed to the environment object, which encapsulates all the simulator functionalities
    env = Environment(client,sim_params_min,sim_params_max,sim_params_nominal,workflow_xml_path,True)
    env.sim_start()
    for action in action_sequence:
        print("\n next action: "+action)
        env.sim_step(action, parameters)
    env.sim_stop()
