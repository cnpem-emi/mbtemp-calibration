from serial import Serial
import numpy as np

global address
global channel
global n_readings

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

    print(answer)

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

def ReadADvalue(add, channel):
    ans = SendReceiveMessage([add, 0x10, 0x00, 0x01, channel])
    if ans is not str:
        return (ans[4]*256 + ans[5]) #% 0x8000

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
n_readings = 5
temperatures = [25, 30, 35]

print("Default parameters for calibration are:")
print("MBTemp address: {:X}".format(address))
print("MBTemp channel: {:d}".format(channel))
print("T1 = {:02f}°, T2 = {:02f}°, T3 = {:02f°}".format(temperatures[0], temperatures[1], temperatures[2]))
print("Samples for each temperature: {:d}".format(n_readings))

if input("Press [Enter] to continue or [n] to change") == "n":
    address = int(input("MBTemp address = 0x"), 16)
    channel = int(input("Channel = 0x"), 16)
    temperatures[0] = float(input("T1 = "))
    temperatures[1] = float(input("T2 = "))
    temperatures[2] = float(input("T3 = "))
    n_readings = int(input("# of samples = ")) 

#SetReadMode(address, channel)
SetReadAD(address, 0x01)
print(SendReceiveMessage([1, 0x10, 0, 1, 0x0b, 0xe3]))
print(SendReceiveMessage([1, 0x10, 0, 1, 0x0c, 0xe2]))


ADvalues = []
y = []
for t in temperatures:
    input('Start {:d}º readings? (press Enter to continue)'.format(t))
    for n in range(n_readings):
        ADvalues.append(ReadADvalue(address, channel))
        y.append(t)

print("ADVALUES:", ADvalues)

x = np.array(ADvalues)
A = np.vstack([x, np.ones(len(x))]).T
y = np.array(y)
print(A)
print(y)
m, c = np.linalg.lstsq(A, y, rcond = -1)[0]
k = round(1/m, 2)
b = round(-c, 2)
print('k = ', k)
print('b = ', b)

WriteAngCoef(address, int(100*k))
WriteLinCoef(address, int(100*b))

print(ReadAngCoef(address))
print(ReadLinCoef(address))


##############################################################################
#TEMPERATURE READINGS

input("Read temperatures?")

#SetReadMode(address, 0x08)
SetReadAD(address, 0x00)
print(SendReceiveMessage([1, 0x10, 0, 1, 0x0b, 0xe3]))
print(SendReceiveMessage([1, 0x10, 0, 1, 0x0c, 0xe2]))



while(1):
    input("Read temperature? (Enter to continue)")
    print("T = {:02f}°".format(ReadTemp(address, channel)))


'''
print("TEMP:", "".join(hex(byte) for byte in ReadTemp(0x01, 0x00)))
for alpha in ReadAlpha(0x01):
    print("ALPHA:", "".join(hex(byte) for byte in alpha))

for k in ReadAngCoef(0x01):
    print("ANGULAR:", "".join(hex(byte) for byte in k))

for b in ReadLinCoef(0x01):
    print("LINEAR:", "".join(hex(byte) for byte in b))
#print("".join(hex(byte) for byte in SendReceiveMessage([0x01, 0x10, 0x00, 0x01, 0x00])))
'''
