
# Joseph Kessler
# 2024 Jan 19
# CanReceive_Tests.py
################################################################################
#     This script tests components of the can parser.

import pandas
import can
import time
import humanize

import numpy as np
import multiprocessing
import zipfile
import io

import bitstring
import CanReceive, SensorDefs

import csv
import re

def timed(function):
    def timed_wrapper(*args, **kwargs):
        t0 = time.time_ns()
        result = function(*args, **kwargs)
        t1 = time.time_ns()
        print("Took", humanize.metric((t1-t0)*1e-9, unit='s'))
        print()
        return result
    return timed_wrapper

################################################################################
############################### Can parsing code ###############################
################################################################################

# Abstract file IO container class.
# Defines an entry generator and a line parsing 
class CanReader:
    def generate_entries(opened_file):
        raise NotImplementedError()
    
    def prep_format(line):
        raise NotImplementedError()

# Can dump with ID 58
#   can0  08EF003A   [5]  19 C0 3C 19 E6
class Candump(CanReader):
    # Generator for handling candump reads.
    def generate_entries(opened_file):#generate_candump_entries(opened_file):
        for line in opened_file:
            line = line[:-1]
            yield line

    # Converts a candump line into a prepared packet.
    def prep_format(line):
        items = list(filter(None, line.split(' ')))
        channel, msg_id, argc, argv = items[0], items[1], items[2][1:-1], items[3:]
        msg_data = ''.join(argv)
        return msg_id, msg_data

class Coolterm(CanReader):
    # Generator for handling coolterm reads.
    # Newlines appear to be in random places.  I'll have to write my own here.
    def generate_entries(opened_file):
        def read_until(gen, char='\n'):
            result = ""
            for c in gen:
                if c == char:
                    break
                result += c
            return result

        def gen_chunk(gen):
            while True:
                header = read_until(gen, ':')
                body = [read_until(gen, ',') for i in range(8)]
                chunk = ':'.join([header, ','.join(body)])
                if header.strip() == "":
                    break
                yield chunk
        
        for line in filter(None, opened_file):
            # The first item is always the id/timestamp, followed by 8 entries.
            gen = (c for c in line[:-1])
            for chunk in gen_chunk(gen):
                yield chunk

    # Converts a coolterm line into a prepared packet.
    def prep_format(line):
        try:
            items = line.replace(':', ',').split(',')
            items[0] = bitstring.BitArray(uint=items[0], length=32).hex
            items[1:] = list(map(lambda x: bitstring.BitArray(uint=x, length=8).hex, items[1:]))
            msg_id, msg_data = items[0], ''.join(items[1:])
        except Exception as e:
            globals().update(locals())
            raise e
        return msg_id, msg_data

################################################################################
################################################################################
################################################################################

class Driver:
    def prep(msg_id, msg_data):
        raise NotImplementedError()
    
    def parse(line):
        raise NotImplementedError()
    
    def post():
        raise NotImplementedError()
    
class RD2(Driver):
    def __init__(self):
            self.canrecieve = CanReceive.CanReceive('virtual', 'virtual')

    def prep(msg_id, msg_data):
        arr = [int('0'+msg_data[i:i+2], base=16) for i in range(0, len(msg_data), 2)]

        msg_out_id = int('0'+msg_id, base=16)
        msg_out_data = bytearray(arr)
        msg_out = can.Message(arbitration_id=msg_out_id, data=msg_out_data)

        return msg_out
    
    def parse(msg_in):
        # Grabs Message ID
        msg_id = int(msg_in.arbitration_id)
        #msg_id_bin = str(bitstring.BitArray(int=msg_id, length=32).bin)
        msg_id_bin = '{0:032b}'.format(msg_id)
        ID_A_bin = msg_id_bin[-11:]
        #ID_A = ba2int(bitarray(ID_A_bin))
        ID_A = int('0'+ID_A_bin, base=2)
        # Grabs the data in the msg
        data_list_hex = msg_in.data.hex()
        #data_bin = bitstring.BitArray(hex=data_list_hex).bin
        data_bin = ''
        for h in data_list_hex:
            data_bin += '{0:04b}'.format(int('0'+h, base=16))
        
        return ID_A, msg_id_bin, data_bin, data_list_hex


@timed
def get_entry_size(name, file, fmt, drv):
    num = 0
    print("Finding total number of entries in %s..."%name)
    file.seek(0)
    for i,line in enumerate(fmt.generate_entries(file)):
        num = i
    file.seek(0)
    return num

@timed
def prep_preprocess(name, file, fmt, drv):
    print("Preparing lines for multiprocessing...")
    file.seek(0)
    prepped = [[line, fmt.prep_format, drv.prep, drv.parse] for line in fmt.generate_entries(file)]
    print(len(prepped))
    return prepped

def preprocess(args):
    line, prep_format, prep, parse = args
    return parse(prep(*prep_format(line)))

@timed
def run_preprocess(lines):
    cores = multiprocessing.cpu_count()
    print("Preprocessing lines on %d cores..."%cores)
    with multiprocessing.Pool(cores) as pool:
        preprocessed = pool.map(preprocess, lines)
        #preprocessed = pool.map(drv.batch, lines)
    return preprocessed

# This file is 160mb.  Please be careful running this script.
def parse_raw_candump(name, file, fmt, drv):
    print("Running tests for %s."%name)
    maxlines = get_entry_size(name, file, fmt, drv)
    preprocessed = run_preprocess(prep_preprocess(name, file, fmt, drv))
    print(f'{len(preprocessed) = }')


    canrecieve = CanReceive.CanReceive('virtual', 'virtual')
    pct = 0
    for i, (ID_A, msg_id_bin, data_bin, data_list_hex) in enumerate(preprocessed):
        p = int(100*i/maxlines)
        if 5 <= p - pct:
            pct += 5
            print("%i%%"%pct)

        canrecieve.translateMessage(ID_A, msg_id_bin, data_bin, data_list_hex)
    
    return canrecieve

################################################################################
# There are two primary test files: a Coolterm Capture, and a very large can
# dump.  The can dump extraction is performed here, before other imports.

# Opens .txt and .zip files.
# paths is a list of strings to test files.
# https://www.geeksforgeeks.org/with-statement-in-python/

class lazy_open:
    def __init__(self, path):
        self.path = path

    def __enter__(self):

        FileName = self.path.replace('\\','/').split('/')[-1]
        Type = FileName.split('.')[-1]
        Name = FileName[:-1-len(Type)]
        
        if Type == 'txt':
            self.file = open(self.path, 'r')
            return ((self.file, FileName),)
        
        elif Type == 'zip':
            with open(self.path, 'rb') as file:
                self.file = zipfile.ZipFile(io.BytesIO(file.read()))

            def generator(zipped):
                for name in zipped.namelist():
                    unzipped = zipped.read(name).decode()
                    yield io.StringIO(unzipped), name

            return generator(self.file)

        else:
            raise NotImplementedError("Filetype unsupported.")

    def __exit__(self, *exceptionArgs):
        self.file.close()

def filter_format(name):
    fmt, drv = None, None

    # Filter format
    if 'CanDump' in name:
        fmt = Candump
    elif 'CoolTerm' in name:
        fmt = Coolterm
    else:
        raise KeyError()
    
    # Filter driver
    if 'HRC' in name:
        raise KeyError()
    else:
        drv = RD2
    
    return fmt, drv


def graphs(canrecieve):
    import numpy as np
    import matplotlib.pyplot as plt
    #time_entry = np.array([item[0] for item in canrecieve2.timeLedger])
    #time_value = np.array([item[1] for item in canrecieve2.timeLedger])
    #plt.plot(time_entry, time_value-time_value[0], 'o-')

    def showsensor(ax, sensor=52, t0=0):
        print("sensor", sensor)
        m, b = 1, 0
        labelSuffix = ""
        if sensor%2 == 1: # Converted value!
            sensor = sensor - 1
            #print(sensor + 1, "converted to", sensor)
            m, b = SensorDefs.sensorList[SensorDefs.sensor_index_from_id[sensor]][2]
            labelSuffix = " converted"
        ledger = canrecieve.sensorLedgers[sensor]
        ledger = np.array(ledger)
        print("ledger shape", ledger.shape)
        sens_time, sens_value = ledger.T
        sens_value = sens_value*m + b
        ax.plot((sens_time - t0)*1000, sens_value, label=SensorDefs.sensor_name_from_id[sensor] + labelSuffix)

    t0 = 578.4427533519122
    fig, ax = plt.subplots()
    #for sensor in [52, 50, 58, 54, 60, 56]:
    #for sensor in [52, 50, 62, 64, 66, 68]:
    for sensor in [62, 64, 52, 50, 60, 58, 54, 66, 68]:
        #showsensor(ax, sensor, t0)
        showsensor(ax, sensor+1, t0)
    ast = np.array(canrecieve.AutosequenceLedger)
    #ax.plot(ast.T[0] - t0, ast.T[1]*10, 'o-', label="Autosequence")
    ax.legend()
    ax.set_xlabel('milliseconds')
    ax.set_ylabel('PSI')
    #ax.set_xbound(-1000, 12000)
    plt.show()


#TJ 5/31 
#candump to csv
if __name__ == "__main__":
    m, b = 1, 0
    with lazy_open(r'CoolTerm_Capture_2022-09-17_17-29-51.txt') as files: 
        for file, name in files:
            print(name)
            
            canrecieve = parse_raw_candump(name, file, *filter_format(name))
            for sensor in  [62, 64, 52, 50, 60, 58, 54, 66, 68]:
                dataframe = pandas.DataFrame()
                m, b = SensorDefs.sensorList[SensorDefs.sensor_index_from_id[sensor]][2]#!!!
                ledger = canrecieve.sensorLedgers[sensor]
                ledger = np.array(ledger)
                #print("ledger shape", ledger.shape)
                sens_time, sens_value = ledger.T
                sens_value = sens_value*m + b
                print("sensor " , sensor)
                print ("sens time " , len(sens_time))
                print("sens val " , len(sens_value))
                print("time raw")
                print(sens_time)
                if dataframe.empty: #if empty add the time column
                    dataframe['Time'] = sens_time.tolist()
                dataframe["PSI"] = sens_value.tolist()
                print(dataframe)
                dataframe.to_csv("_"+ str(SensorDefs.sensor_name_from_id[sensor]) + '.csv', index=False)
                
        
        
        print("end")

if(False):
    #with lazy_open(r'C:\Users\Joe\Downloads\lazy_read_test.zip') as files:
    with lazy_open(r'staticfireCanDump-1-21-2023.zip') as files:
        for file, name in files:
            print(name)
            with file:
                graphs(parse_raw_candump(name, file, *filter_format(name)))


        fileName = input("Please copy and paste the name of the .txt file (do not include extension): ")
        writeTo = fileName + '.csv'

        with open(writeTo, 'w', newline='') as file:
            writer = csv.writer(file)
            field = ["Time", "State", "Lox High", "Fuel High", "Lox Dome", "Fuel Dome", "Lox Tank1",
                    "Lox Tank2", "Fuel Tank1", "Fuel Tank2"]
        
            #writer.writerow(field)
            #for #iterate through time
                #row = [CanReceive.]
                #for sensor in [62, 64, 52, 50, 60, 58, 54, 66, 68]: #iterate through sensors and collect into a row then write
                    #writer.writerow

