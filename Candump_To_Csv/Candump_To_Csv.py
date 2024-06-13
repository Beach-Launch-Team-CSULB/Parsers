'''
TJ Malaska
Jun 8
Converts candump into csv
'''

import csv
import pandas

#important CAN IDs
PROP_STATE_REPORT = 127
ENGINE_STATE_REPORT = 128

#Command msgs
cmdID = {
    0: "ABORT",
    1: "VENT",
    2: "FIRE",
    3: "Tank PRESS",
    4: "STANDBY",
    5: "PASSIVE",
    6: "TEST"
}
#Sensor report
sensorID = {        #2 bytes will be one raw sensor value
    129: ["Lox High", "Fuel High", "Lox Dome", "Fuel Dome"],        #Prop Node Sensors 1-4
    130: ['Lox Tank1', 'Lox Tank2', 'Fuel Tank1', 'Fuel Tank2'],    #Prop Node Sensors 5-8  
    131: ['Pneumatics', 'Lox Inlet', 'Fuel Inlet', 'Fuel Injector'],#Eng Node Sensors 1-4 
    132: ['Chamber1', 'Chamber2']         #Eng Node Sensors 5-8 
}

#--------------------------------------------------------------
data = {'Time' : [], "State": [], "Lox High": [], "Fuel High": [], "Lox Dome": [], "Fuel Dome": [], "Lox Tank1": [], "Lox Tank2": [], "Lox Tank2": [],\
    "Fuel Tank1": [], "Fuel Tank2": [], "Pneumatics": [], "Lox Inlet": [], "Fuel Inlet": [], "Fuel Injector": [], "Chamber1": [], "Chamber2": []}

df = pandas.DataFrame(data)

canDump = open("WaterflowCANDump.txt", "r")
newLine = {
    'Time' : -1, "State": -1, "Lox High": -1, "Fuel High": -1, "Lox Dome": -1, "Fuel Dome": -1, "Lox Tank1": -1, "Lox Tank2": -1, "Lox Tank2": -1,\
        "Fuel Tank1": -1, "Fuel Tank2": -1, "Pneumatics": -1, "Lox Inlet": -1, "Fuel Inlet": -1, "Fuel Injector": -1, "Chamber1": -1, "Chamber2": -1
} 

def readSensor(line):
    name = None
    for I in range(len(sensorID[int(line[1], 16)])):
        rawVal = line[3 + I] + line[4 + I]
        newLine[sensorID[int(line[1], 16)][I]] = int(rawVal,16)
    return 1
print("Starting parse")
for line in canDump:
    line = line.split()
    if line[0] == "can0":            #skipping weird null lines (null line ID seems to be 129 so we are missing propNode1)
        if int(line[1], 16) in cmdID.keys():        # if a state change
            newLine["State"] = int(line[1], 16) 

        if int(line[1], 16) in sensorID.keys():     # if sensor reading 
            readSensor(line)
        
        if int(line[1], 16) in [128]:    #if engine node state report 
            newTime = line[3] + line[4] + line[5] + line[6]
            newLine['Time'] = int(newTime, 16)
            newLine['State'] = int(line[7], 16)
            df = df._append(newLine, ignore_index = True)   #add newline

df.to_csv("WaterflowCANDump" + '.csv', index=False)
print("Done!")
