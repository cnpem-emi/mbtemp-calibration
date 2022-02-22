from serial import Serial

global connection = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)

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
    # after read the first byte, set the timeout to 100ms
    connection.timeout = 0.1
    # keep reading bytes until timeout exceed
    while next_byte != b"":
	answer.append(ord(next_byte))
	next_byte = connection.read(1)

    if answer == []:
        return "Timeout passed"
    else:
        answer_len = len(answer)
        answer_checksum = 0;
        for i in range (answer_len - 1):
            answer_checksum += ord(answer[i])

        # sum checksum_answer with last byte of message and compare with 0x00
        if (answer_checksum + ord(answer[answer_len - 1])) % 0x100 != 0:
            return "Message corrupted"
        else:
            return (answer)

print(SendReceiveMessage([0x01, 0x10, 0x00, 0x01, 0x00]))
