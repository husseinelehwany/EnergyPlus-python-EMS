# This script is an intro to the Energyplus Python API
# It demonestrates how to run energyplus from a python script
# Prepared by Hussein Elehwany 20/07/2023
import sys
sys.path.insert(0, 'C:\EnergyPlusV23-1-0')  # add E-Plus directory to path to be able to import API
from pyenergyplus.api import EnergyPlusAPI #import EnergyPlus library

def my_callback_function(state):
    # global variables are necessary as the callback function takes only one input: state
    global heatingSch_hndl, coolingSch_hndl,heatingSP_hndl,coolingSP_hndl,indoorT_hndl,outdoorT_hndl,heat_coil_hndl, handleDone
    # get handles
    if not handleDone:
        if api.exchange.api_data_fully_ready(state):
            heatingSch_hndl = api.exchange.get_actuator_handle(state, "Schedule:Constant", "Schedule Value", "HeatingSch")
            coolingSch_hndl = api.exchange.get_actuator_handle(state, "Schedule:Constant", "Schedule Value", "CoolingSch")
            heatingSP_hndl = api.exchange.get_actuator_handle(state, "Schedule:Constant", "Schedule Value", "hSP")
            coolingSP_hndl = api.exchange.get_actuator_handle(state, "Schedule:Constant", "Schedule Value", "cSP")
            outdoorT_hndl = api.exchange.get_variable_handle(state,'Site Outdoor Air Drybulb Temperature', 'Environment')
            indoorT_hndl = api.exchange.get_variable_handle(state,'Zone Mean Air Temperature', 'Zone1')
            heat_coil_hndl = api.exchange.get_meter_handle(state,'HeatingCoils:EnergyTransfer')
            if -1 in [heatingSch_hndl, coolingSch_hndl, indoorT_hndl, heat_coil_hndl]:
                sys.exit(1)
            handleDone = True
        else:
            return
    
    # exchange information with EnergyPlus
    month = api.exchange.month(state) 
    
    # read variables
    outdoor_temp = api.exchange.get_variable_value(state, outdoorT_hndl)
    indoor_temp = api.exchange.get_variable_value(state, indoorT_hndl)
    # print(indoor_temp, outdoor_temp)
    
    # read meters
    heating_coils = api.exchange.get_meter_value(state, heat_coil_hndl)
    
    # change setpoints
    api.exchange.set_actuator_value(state, heatingSP_hndl, 20)
    api.exchange.set_actuator_value(state, coolingSP_hndl, 25)
    
    # actuate
    if month < 4 or month > 10:
        api.exchange.set_actuator_value(state, heatingSch_hndl, 1)
        api.exchange.set_actuator_value(state, coolingSch_hndl, 0)
    else:
        api.exchange.set_actuator_value(state, heatingSch_hndl, 0)
        api.exchange.set_actuator_value(state, coolingSch_hndl, 1)
    
    


# initializations
heatingSch_hndl = 0
coolingSch_hndl = 0
heatingSP_hndl = 0
coolingSP_hndl = 0
outdoorT_hndl = 0
indoorT_hndl = 0
heat_coil_hndl = 0
handleDone = False

# initialize EPlus
api = EnergyPlusAPI()

#instance of the simulation
state = api.state_manager.new_state() 

# energyplus model calling point, callback function
api.runtime.callback_begin_system_timestep_before_predictor(state , my_callback_function)

# run EPlus
epwFile = 'ON_OTTAWA-INTL-ONT_716280_19.epw'
idfFile = 'Shoebox.idf'
output_folder = 'out'
# -x short form to run expandobjects for HVACtemplates. see EnergyPlusEssentials.pdf p16
cmd_args = ['-w',epwFile, '-d', output_folder,'-x',idfFile]
api.runtime.run_energyplus(state,cmd_args)

# delete state after simulation to free the memory
api.state_manager.delete_state(state)

print("Handles done: {}".format(handleDone))



