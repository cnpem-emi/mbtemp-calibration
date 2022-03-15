from serial import Serial
import numpy as np
import time

global address
global channel
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

def ReadADvalue(add, channel):
    ans = ""
    attempts = 0
    while type(ans) is str:
        ans = SendReceiveMessage([add, 0x10, 0x00, 0x01, channel])
        attempts += 1
        if attempts >= 10:
            print("ERROR: ", ans)
            time.sleep(3)
    return (ans[4]*256 + ans[5])

def ReadAlpha(add):
    alphas = []
    for id in [0x08, 0x0D, 0x10]:
        alphas.append(SendReceiveMessage([add, 0x10, 0x00, 0x01, id]))
    return alphas

def ReadAngCoef(add):
    angs = []
    for id in [0x09, 0x0E, 0x11]:
        angs.append(SendReceiveMessage([add, 0x10, 0x00, 0x01, id]))
    return angs

def ReadLinCoef(add):
    lins = []
    for id in [0x0A, 0x0F, 0x12]:
        lins.append(SendReceiveMessage([add, 0x10, 0x00, 0x01, id]))
    return lins

def WriteAlpha (add, value):
    MS_byte = value//256
    LS_byte = value%256
    answer = SendReceiveMessage([add, 0x20, 0x00, 0x03, 0x08, MS_byte, LS_byte])
    return answer

def WriteAngCoef (add, value):
    MS_byte = value//256
    LS_byte = value%256
    answer = SendReceiveMessage([add, 0x20, 0x00, 0x03, 0x09, MS_byte, LS_byte])
    return answer

def WriteLinCoef (add, value):
    MS_byte = value//256
    LS_byte = value%256
    answer = SendReceiveMessage([add, 0x20, 0x00, 0x03, 0x0A, MS_byte, LS_byte])
    return answer

def SetReadAD(add, mode):
    answer = SendReceiveMessage([add, 0x20, 0x00, 0x02, 0x0B, mode])
    return answer

def SetReadMode(add, channel):
    answer = SendReceiveMessage([add, 0x20, 0x00, 0x02, 0x0C, channel])
    return answer

#######################################################################
# CALIBRATION PROCEDURE
address = 0x01
channel = 0x00
n_samples = 30
temperatures = [20.0, 25.0, 30.0]

# print calibration parameters
print("=====================================================")
print("Default parameters for calibration are:")
print("MBTemp address: 0x{:02X}".format(address))
print("MBTemp channel: 0x{:02X}".format(channel))
print("T1 = {:.2f}°C, T2 = {:.2f}°C, T3 = {:.2f}°C".format(temperatures[0], temperatures[1], temperatures[2]))
print("# of samples for each temperature: {:d}".format(n_samples))

# change calibration parameters
if input("Press [Enter] to continue or [n] to change: ") == "n":
    #print("=================================================")
    print("\nSet parameters for calibration:")
    address = int(input("MBTemp address = 0x"), 16)
    channel = int(input("Channel = 0x"), 16)
    temperatures[0] = float(input("T1 = "))
    temperatures[1] = float(input("T2 = "))
    temperatures[2] = float(input("T3 = "))
    n_samples = int(input("# of samples = "))

# set MBTemp to read AD values
SetReadAD(address, 0x01)
time.sleep(2)
#print(SendReceiveMessage([1, 0x10, 0, 1, 0x0b, 0xe3])) #ckeck setting variable


# read AD values
ADvalues = []
y = []
print("")
for t in temperatures:
    input('Start readings for {:.2f} °C? (press Enter to continue)'.format(t))
    print("wait...")
    for n in range(n_samples):
        ADvalues.append(ReadADvalue(address, channel))
        y.append(t)
        time.sleep(0.1)
#print("ADVALUES:", ADvalues)

# coefficients calculation
x = np.array(ADvalues)
A = np.vstack([x, np.ones(len(x))]).T
y = np.array(y)
m, c = np.linalg.lstsq(A, y, rcond = -1)[0]
k = round(1/m, 2)
b = round(-c, 2)
print("")
print("k = ", k)
print("b = ", b)

# write calculated coefficients to MBTemp
WriteAngCoef(address, int(100*k))
WriteLinCoef(address, int(100*b))

# ckeck written coefficients
#print(ReadAngCoef(address))
#print(ReadLinCoef(address))


##############################################################################
#TEMPERATURE READINGS

input("\nRead temperatures? (Enter to continue)")

# set MBTemp to read temperatures
SetReadAD(address, 0x00)
time.sleep(2)
#print(SendReceiveMessage([1, 0x10, 0, 1, 0x0b, 0xe3])) #check setting variable

while(1):
    input("Read new temperature?")
    print("T = {:.2f} °C".format(ReadTemp(address, channel)))
