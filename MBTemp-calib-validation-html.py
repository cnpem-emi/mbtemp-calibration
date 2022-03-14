from serial import Serial
import numpy as np
import json
import csv
import math

global address
global n_samples
global connection

#connection = Serial("/dev/ttyUSB0", 115200, timeout=1)

def SendReceiveMessage(msg): #integer arguments
    msg_sum = 0
    for i in msg:
        msg_sum += i
    checksum = (0x100 - (msg_sum % 0x100)) % 0x100

    msg.append(checksum)
    connection.reset_input_buffer()
    connection.write(bytes(msg))

    answer = []
    next_byte = connection.read(1)
    connection.timeout = 0.1
    while next_byte != b"":
        answer.append(ord(next_byte))
        next_byte = connection.read(1)

    #print(answer)

    if answer == []:
        return "Timeout passed"
    else:
        answer_len = len(answer)
        answer_checksum = 0;
        for i in range (answer_len - 1):
            answer_checksum += answer[i]

        if (answer_checksum + answer[answer_len - 1]) % 0x100 != 0:
            return "Message corrupted"
        else:
            return answer

def ReadTemp(add, channel):
    ans = SendReceiveMessage([add, 0x10, 0x00, 0x01, channel])
    if ans is not str:
        #print(temp)
        return (ans[4]*256 + ans[5])/100

#######################################################################
# VALIDATION PROCEDURE
address = 0x01
n_samples = 20
temperatures = [25.0, 30.0, 35.0]

# print validation parameters
print("=====================================================")
print("Default parameters for validation are:")
print("MBTemp address: 0x{:02X}".format(address))
print("T1 = {:.2f}°C, T2 = {:.2f}°C, T3 = {:.2f}°C".format(temperatures[0], temperatures[1], temperatures[2]))
print("# of samples for each temperature: {:d}".format(n_samples))


# change calibration parameters
if input("Press [Enter] to continue or [n] to change: ") == "n":
    #print("=================================================")
    print("\nSet parameters for calibration:")
    address = int(input("MBTemp address = 0x"), 16)
    temperatures[0] = float(input("T1 = "))
    temperatures[1] = float(input("T2 = "))
    temperatures[2] = float(input("T3 = "))
    n_samples = int(input("# of samples = "))


# read temperatures
samples = []
samples_ht = []
t_high = 120
print("")


'''
for channel in range(2):
    input('Start readings for channel {:d}? (press Enter to continue)'.format(channel))
    samples.append([])
    for t in range(len(temperatures)):
        samples[channel].append([])
        input('\tStart readings for {:.2f} °C? (press Enter to continue)'.format(temperatures[t]))
        for n in range(n_samples):
            samples[channel][t].append(ReadTemp(address, channel))

    # read high temperature for channel 1:
    if channel == 0:
        input('\tStart readings for {:d} °C? (press Enter to continue)'.format(t_high))
        for n in range(n_samples):
            samples_ht.append(ReadTemp(address, 0))

'''
# random samples
samples.append([[24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.65, 24.65, 24.65, 24.65, 24.66, 24.66, 24.66], [28.83, 28.83, 28.83, 28.83, 28.83, 28.83, 28.83, 28.83, 28.83, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82], [32.89, 32.89, 32.89, 32.89, 32.89, 32.89, 32.88, 32.88, 32.88, 32.88, 32.9, 32.9, 32.9, 32.9, 32.9, 32.9, 32.9, 32.9, 32.9, 32.9]])
samples.append([[24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.66, 24.65, 24.65, 24.65, 24.65, 24.66, 24.66, 24.66], [28.83, 28.83, 28.83, 28.83, 28.83, 28.83, 28.83, 28.83, 28.83, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82, 28.82], [32.89, 32.89, 32.89, 32.89, 32.89, 32.89, 32.88, 32.88, 32.88, 32.88, 32.9, 32.9, 32.9, 32.9, 32.9, 32.9, 32.9, 32.9, 32.9, 32.9]])
#samples.append([[26.82, 26.82, 26.85, 26.85, 26.85, 26.85, 26.88, 26.88, 26.88, 26.88, 26.92, 26.92, 26.92, 26.92, 26.92, 26.96, 26.96, 26.96, 26.96, 27.01], [31.71, 31.71, 31.7, 31.7, 31.7, 31.7, 31.69, 31.69, 31.69, 31.69, 31.69, 31.69, 31.69, 31.69, 31.69, 31.69, 31.69, 31.69, 31.69, 31.69], [36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.25, 36.24, 36.24]])
samples_ht = [122.78,122.30,122.12,122.76,122.01,122.19,122.98,122.29,122.02,122.59,122.06,122.53,122.11,122.58,122.29,122.31,122.36,122.68,122.58,122.79]


# generate dataset
data = []
for ch in range(2):
    data.append([])
    for i in range(len(temperatures)):
        for j in range(n_samples):
            data[ch].append({"x": temperatures[i], "y": samples[ch][i][j]})
#print(data)

data_hist = []
T_min = temperatures[0]
T_max = temperatures[2]

for ch in range(2):
    data_hist.append([])
    for t in range(3):
        t_min = math.floor(min(samples[ch][t]))
        t_max = math.ceil(max(samples[ch][t]))
        bins = [float(x) for x in np.arange(t_min, t_max, 0.01)]
        density = [int(x) for x in np.histogram(samples[ch][t], bins = bins)[0]]
        T_min = min([T_min, t_min])
        T_max = max([T_max, t_max])
        for i in range(len(density)):
            data_hist[ch].append({"x": round(bins[i], 2), "y": density[i]})
#print(data_hist)



# plot on html file
html = ""

with open("template.html", "r") as f:
    html = f.read()

    for ch in range(2):
        html = html.replace("${"+str(ch)+"}", json.dumps(data_hist[ch]))
        html = html.replace("${"+str(ch+8)+"}", json.dumps(data[ch]))
        html = html.replace("${labels}", json.dumps([round(float(x), 2) for x in np.arange(T_min, T_max, 0.01)]))
        html = html.replace("${scatter_labels}", json.dumps([x for x in range(math.floor(temperatures[0])-1, math.ceil(temperatures[2])+1, 1)]))

with open("out.html", "w") as f:
    f.write(html)



# write data into csv
with open("dataset.csv", "w") as f:
    writer = csv.writer(f)

    writer.writerow(["channel", "temperature", "mean", "std deviation"])
    for ch in range(2):
        for t in range(3):
            writer.writerow([ch, temperatures[t], round(np.mean(samples[ch][t]), 2), round(np.std(samples[ch][t]), 2)])


    writer.writerow(["channel", "real temperature", "temperature read"])
    for ch in range(2):
        for t in range(3):
            for i in range(n_samples):
                writer.writerow([ch, temperatures[t], samples[ch][t][i]])
    writer.writerow([0, t_high, round(np.mean(samples_ht), 2)])
