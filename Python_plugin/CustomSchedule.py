# this script is called by Shoebox.idf
# Intro to the Energyplus Python API
# It demonestrates how to use variable, meters and actuators
# Prepared by Hussein Elehwany 20/07/2023

from pyenergyplus.plugin import EnergyPlusPlugin # import plugin
import sys
import time
print(sys.version)

class HVACAvailability(EnergyPlusPlugin): # class name, as defined in .idf file

    def on_begin_timestep_before_predictor(self, state) -> int:  # energyplus model calling point        
        # check if API ready
        if self.api.exchange.api_data_fully_ready(state):
            # get handles
            if 'handles_done' not in self.data:  # check if handles_done because handles are assigned only once
                # get cooling actuator handle
                self.actuator_cooling = self.api.exchange.get_actuator_handle(
                    state, "Schedule:Constant", "Schedule Value", "CoolingSch")
                # check if actuator was found successfully 
                if self.actuator_cooling == -1:
                    self.api.runtime.issue_severe(state, "Could not get handle to cooling setpoint schedule")
                    return 1
                
                # get heating actuator handle
                self.actuator_heating = self.api.exchange.get_actuator_handle(
                    state, "Schedule:Constant", "Schedule Value", "HeatingSch")
                # check if actuator was found successfully 
                if self.actuator_heating == -1:
                    self.api.runtime.issue_severe(state, "Could not get handle to heating setpoint schedule")
                    return 1
                
                # get handle for Zone Mean Air Temperature 
                self.variable_temperature = self.api.exchange.get_variable_handle(
                    state,'Zone Mean Air Temperature', 'Zone1')
                # check if actuator was found successfully 
                if self.variable_temperature == -1:
                    self.api.runtime.issue_severe(state, "Could not get handle to Zone Mean Air Temperature")
                    return 1
                
                # get handle for heating coils meter
                self.meter_heat_coil = self.api.exchange.get_meter_handle(state,'HeatingCoils:EnergyTransfer')
                # check if actuator was found successfully 
                if self.meter_heat_coil == -1:
                    self.api.runtime.issue_severe(state, "Could not get handle to heating coils meter")
                    return 1            
                
            
                self.data['handles_done'] = True
        
            # exchange information with EnergyPlus 
            month = self.api.exchange.month(state) 
            
            # read variables
            indoor_temp = self.api.exchange.get_variable_value(state, self.variable_temperature)
            #print(indoor_temp)
            
            # read meters
            heating_coils = self.api.exchange.get_meter_value(state, self.meter_heat_coil)
            
            # actuate
            if month > 4 and month < 10:
                self.api.exchange.set_actuator_value(state, self.actuator_cooling, 1)
                self.api.exchange.set_actuator_value(state, self.actuator_heating, 0)
            else:
                self.api.exchange.set_actuator_value(state, self.actuator_cooling, 0)
                self.api.exchange.set_actuator_value(state, self.actuator_heating, 1)
        return 0


