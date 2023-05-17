import serial
import serial.tools.list_ports
import time
import configparser
import argparse

def decodeValue(value):
    value = value.strip().replace(b'\n', b' ').replace(b'\r', b' ')
    return value.decode("utf-8")

def sendState(arduino, state: int) -> None:
    arduino.write(bytearray(state.to_bytes(1, 'big')))

def readOp(arduino, config) -> bytearray:
    eepromVal: bytearray = []
    for i in range(0, int(config['DEFAULT']['SizeToRead'])):
        arduino.write(bytes(b'sync'))
        # read(1) takes forever, maybe there is a better solution to it
        val = arduino.read(1)
        eepromVal.append(val)
    return eepromVal


def writeOp(arduino) -> None:
    for b in binData:
        arduino.write(b.to_bytes(1, 'big'))
        arduino.flush()
        # wait for sync
        value = arduino.readline()
        if decodeValue(value) != 'sync':
            raise Exception("Sync broken.")
    print("Finished writing")

def main(state, config, binData:bytearray = []):
    # find arduino port
    port = ''
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Arduino" in p.manufacturer:
            port = p[0]

    if port == '':
        raise Exception("No port was found.")
    arduino = serial.Serial(port=port, baudrate=int(config['DEFAULT']['Baudrate']), timeout=None)
    time.sleep(1)


    # Wait for arduino to approve connection
    value = arduino.readline()
    if decodeValue(value) != str(config['DEFAULT']['ApprovalMessage']):
        raise Exception("Arduino didn't accept the connection.")
    
    sendState(arduino, state)
    if state == int(config['DEFAULT']['ReadingState']):
        return readOp(arduino, config)
    else:
        writeOp(arduino)





if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('eepromProgrammer/config/config.ini')
    state = int(config['DEFAULT']['ReadingState'])
    filename = ''

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', 
                        dest='state', 
                        action='store_const',
                        const=int(config['DEFAULT']['ReadingState']),
                        help='Read from EEPROM')
    parser.add_argument('-w', 
                        dest='state', 
                        action='store_const',
                        const=int(config['DEFAULT']['WritingState']),
                        help='Write to EEPROM')

    parser.add_argument('-f',
                        required=False,
                        dest='filename',
                        type=str,
                        help='Enter filename if in-/output should be read/saved to a file')

    parser.add_argument('-a',
                        required=False,
                        dest='amountOfBytes',
                        type=str,
                        help='Enter amount of bytes to read. Just necessary in read mode.')
    
    args = parser.parse_args()
    
    state = args.state
    filename = args.filename
    binData: bytearray = []
    if (args.amountOfBytes is not None):
        config['DEFAULT']['SizeToRead'] = args.amountOfBytes

    if filename is None and state == int(config['DEFAULT']['WritingState']):
        print('Filename must be provided if writing state is set')
        exit()
    else:
        f = open("rom.bin", "rb")
        binData: bytearray = f.read()
        f.close()
    try: 
        binData = main(state, config, binData)
        if binData is not None:
            print(binData)
    except Exception as e:
        print("There was an error: ", e)
