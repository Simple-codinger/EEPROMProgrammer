#define WE 7
#define OE 5
#define ERROR_LED 3

#define SIZE_EEPROM 8192
#define SIZE_ADDRESS 13
#define SIZE_IO 8

#define READING_ACTION 0
#define WRITING_ACTION 1


const char ADDR[] = {22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46};
const char IO[] = {53, 51, 49, 47, 45, 43, 41, 39};
unsigned int addressCounter = 0;

byte state = READING_ACTION;
bool error = false;

byte intToByte(unsigned int in, int location){
  return (1&(in>>(location)));
}

void setAddress(unsigned int address, bool outputEnable) {
  for(int i=0; i<SIZE_ADDRESS; i++) {
    digitalWrite(ADDR[i], (bool)intToByte(address, i)?HIGH:LOW);
  }
  digitalWrite(OE, outputEnable?LOW:HIGH);
}

void setupAddressPins() {
  for(int i=0; i<SIZE_ADDRESS; i++){
    pinMode(ADDR[i], OUTPUT);
  }
}

byte readEEPROM(unsigned int address) {
  for(int i=0; i<SIZE_IO; i++){
    pinMode(IO[i], INPUT);
  }
  setAddress(address, true);

  byte data = 0;
  for(int i = SIZE_IO-1; i>= 0; i--){
    data = (data << 1) + digitalRead(IO[i]);
  }
  return data;
}

void writeEEPROM(unsigned int address, byte data) {
  setAddress(address, false);
  for(int i = 0; i < SIZE_IO; i++){
    pinMode(IO[i], OUTPUT);
  }
  for(int i = 0; i < SIZE_IO; i++){
    digitalWrite(IO[i], data & 1);
    data = data >> 1;
  }
  digitalWrite(WE, LOW);
  delayMicroseconds(1);
  digitalWrite(WE, HIGH);
  delay(10);
}

void setup() {
  // put your setup code here, to run once:
  digitalWrite(WE, HIGH);
  pinMode(WE, OUTPUT);
  setupAddressPins();
  state = READING_ACTION;
  addressCounter = 0;
  error = false;

  pinMode(ERROR_LED, OUTPUT);
  digitalWrite(ERROR_LED, LOW);
  
  Serial.begin(57600);
  Serial.println(42);
  
  while(Serial.available() == 0);
  // set state
  byte value = Serial.read();
  state = value;
  //writeEEPROM(1, 6);
  //Serial.println((int)readEEPROM(1));
  //error = true;
}

void loop() {
  if (!error) {
    // check state
    if(state == READING_ACTION){
      // check if sync signal is available
      if (Serial.available() > 0) {
        String value = Serial.readString();
        if (value == "sync") {
          // python is ready to get new byte
          byte eepromVal = readEEPROM(addressCounter++);
          Serial.write(eepromVal);
        } else {
          error = true;
          digitalWrite(ERROR_LED, HIGH);
        }
      }
    } else {
      if (Serial.available() > 0) {
        byte incomingByte = Serial.read();
        writeEEPROM(addressCounter++, incomingByte);
        Serial.println("sync");
      }
    }
    delay(10);
  }
}
