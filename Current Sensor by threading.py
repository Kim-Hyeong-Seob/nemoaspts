import spidev
import time
import os
#pin_number = int(input('Type in the chip pin number you want to use: '))
pin_number =0
# Define delay between readings
iterate_time = int(input('Type Generation Detect Iteration Time (second): '))

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 60

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
    if channel > 7 or channel < 0:
        
        return -1
    adc = spi.xfer([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data, places):
    #return .0264 * data - 13.51
    volts = (data * 5) / float(1023)
    volts = round(volts, places)
    return volts

def ConvertCurrent(data,places):
    current = (ConvertVolts(data,places)-2.5)/0.066
    current = round(current,places)
    return current

while True:
    #for abs_current, this list always initialize in every while sentence start
    abs_current = []

    #check current in 5 seconds
    for i in range(iterate_time) :
        print("hello")
        print(i,"loop")
        # Read the light sensor data
        current_level = ReadChannel(pin_number)
        current_volts = ConvertVolts(current_level, 2)
        current_current = ConvertCurrent(current_level,2)
        # Read the temperature sensor data
        #temp_level = ReadChannel(temp_channel)
        #temp_volts = ConvertVolts(temp_level, 2)
        #temp = ConvertTemp(temp_level, 2)
        # Print out results
        print ("--------------------------------------------")
        print("Light: {} ({}V,{}A)".format(current_level, current_volts,current_current))
        #print("Temp : {} ({}V) {} deg C".format(temp_level, temp_volts, temp))
        
        # Wait before repeating loop
        

        #Collect Current to find that inverter doesn't generate
        current_list = []
        current_list.append(current_current)
        print(current_list)
    
        
        time.sleep(1)
    

    #Calculate avg_abs_current in 5seconds, and if the result too small then inverter doesn't generate.
    for contents in current_list :
        abs_current.append(abs(contents))
        print(abs_current)

    avg_abs_current = sum(abs_current, 0.0)/len(abs_current)
    print(avg_abs_current)

    if avg_abs_current < 1.5 : # this 1.5 must be changed
        print('not generated')
