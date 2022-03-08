from serial import Serial
import numpy as np
import plotly.express as px
import pandas as pd
#import matplotlib.pyplot as plt

global address
global n_samples
global connection

connection = Serial("/dev/ttyUSB0", 115200, timeout=1)

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
y = []
print("")
'''
for channel in range(2):
    input('Start readings for channel {:d}? (press Enter to continue)'.format(channel))
    samples.append([])
    for t in range(len(temperatures)):
        samples[channel].append([])
        input('Start readings for {:.2f} °C? (press Enter to continue)'.format(temperatures[t]))
        for n in range(n_samples):
            samples[channel][t].append(ReadTemp(address, channel))
    print("CHANNEL SAMPLES: ", samples[channel])
print("SAMPLES:", samples)
'''

samples.append([[25.12, 25.02, 25.38, 24.96, 24.96, 25.36, 25, 25.26, 25.06, 25.3, 24.6, 25.18, 24.83, 24.8, 24.63, 24.95, 24.54, 25.02, 24.93, 24.89], [30.33, 29.58, 30.3, 30.3, 29.93, 30.03, 30.04, 29.75, 30.26, 30.01, 30.19, 29.85, 29.87, 30.26, 29.96, 30.3, 29.95, 30.18, 30.17, 30.06], [35.4, 35.34, 35.24, 35.08, 34.58, 35.16, 35.01, 35.01, 34.74, 34.78, 34.85, 35.48, 34.57, 35.02, 34.9, 34.99, 35.29, 35.13, 34.72, 35.14]])
samples.append([[25.24, 24.9, 24.66, 24.84, 25.32, 25.09, 25.09, 25.45, 24.62, 24.81, 25.13, 25.01, 25.14, 24.71, 24.66, 25.4, 25.49, 24.7, 25.39, 24.95], [30.5, 30.14, 29.9, 29.84, 30.21, 30.33, 29.96, 30.43, 30.18, 30.42, 29.89, 29.92, 30.12, 29.73, 30.05, 29.55, 29.54, 30.05, 30.21, 29.96], [35.27, 34.73, 34.8, 34.66, 35, 34.83, 34.78, 34.97, 35.44, 35.06, 34.97, 35.38, 35.13, 35.14, 34.73, 35.31, 34.59, 35.08, 35.18, 34.65]])


# generate dataset
data = {
    "channel": [],
    "t_real": [],
    "t_read": []
}
for ch in range(2):
    for i in range(len(temperatures)):
        for j in range(n_samples):
            data["channel"].append(str(ch))
            data["t_real"].append(temperatures[i])
            data["t_read"].append(samples[ch][i][j])
df = pd.DataFrame(data)
print(df)


# plot
fig1 = px.scatter(df, x = "t_real", y = "t_read", color = "channel", symbol = "t_real")
fig2 = px.histogram(df, x = "t_read", color = "channel", nbins = 60, histnorm = 'probability density', marginal = "rug")
fig1.show()
fig2.show()


# statistics

'''
fig, ax = plt.subplots()
for i in range(len(temperatures)):
    ax.scatter([temperatures[i]]*n_samples, samples[i])
plt.show()
'''
