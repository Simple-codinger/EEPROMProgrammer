
code = bytearray([
    0xea,
    0x6c,
    0x00,
    0xe0
])

rom = code + bytearray([0xea]*(8192 - len(code)))
rom[0x1ffc] = 0x00
rom[0x1ffd] = 0xe0


#rom = bytearray([0xff]*3)
with open("rom.bin", "wb") as out_file:
    out_file.write(rom)