from serial import Serial
import numpy as np
import plotly.express as px
import pandas as pd
import csv
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
    ans = ""
    attempts = 0
    while type(ans) is str:
        ans = SendReceiveMessage([add, 0x10, 0x00, 0x01, channel])
        attempts += 1
        if attempts >= 10:
            print("ERROR: ", ans)
            time.sleep(3)
    return (ans[4]*256 + ans[5])/100

#######################################################################
# VALIDATION PROCEDURE
address = 0x01
n_samples = 20
temperatures = [20, 25, 30]

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

for ch in range(8):
    input('Start readings for channel {:d}? (press Enter to continue)'.format(channel))
    samples.append([])
    for t in range(len(temperatures)):
        samples[ch].append([])
        input('Start readings for {:.2f} °C? (press Enter to continue)'.format(temperatures[t]))
        for n in range(n_samples):
            samples[ch][t].append(ReadTemp(address, channel))

    # read high temperature for channel 1:
    if ch == 0:
        input('Start readings for {:d} °C? (press Enter to continue)'.format(t_high))
        for n in range(n_samples):
            samples_ht.append(ReadTemp(t_high, 0))


# generate dataset
data = {
    "channel": [],
    "t_real": [],
    "t_read": []
}
for ch in range(8):
    for i in range(len(temperatures)):
        for j in range(n_samples):
            data["channel"].append(str(ch))
            data["t_real"].append(temperatures[i])
            data["t_read"].append(samples[ch][i][j])
# high temperature sample
data["channel"].append("{:d} °C".format(t_high))
data["t_real"].append(t_high)
data["t_read"].append(round(np.mean(samples_ht), 2))
df = pd.DataFrame(data)



# plot
fig1 = px.scatter(df, x = "t_real", y = "t_read", color = "channel")
nbins = round((df["t_read"].max() - df["t_read"].min()) / 0.05)
fig2 = px.histogram(df[:len(df)-1], x = "t_read", color = "channel", nbins = nbins, histnorm = 'probability density', marginal = "rug")
fig1.show()
fig2.show()
fig1.write_html("results/scatter.html")
fig2.write_html("results/histogram.html")


# write data into csv
with open("results/dataset.csv", "w") as f:
    writer = csv.writer(f)

    writer.writerow(["channel", "temperature", "mean", "std deviation"])
    for ch in range(8):
        for t in range(3):
            writer.writerow([ch, temperatures[t], round(np.mean(samples[ch][t]), 2), round(np.std(samples[ch][t]), 3)])

    writer.writerow(["channel", "real temperature", "temperature read"])
    for ch in range(8):
        for t in range(3):
            for i in range(n_samples):
                writer.writerow([ch, temperatures[t], samples[ch][t][i]])
    writer.writerow([0, t_high, round(np.mean(samples_ht), 2)])


'''
fig, ax = plt.subplots()
for i in range(len(temperatures)):
    ax.scatter([temperatures[i]]*n_samples, samples[i])
plt.show()
'''
