import sys
import os
import fileinput

arg1 = []  # <type 'list'>: [0, 0, 0, 0, 0, 1, 1, 10, 10, 0, 3, 4, 152, 4, 10, 1, 0, 112, 0]
arg2 = []  # <type 'list'>: [0, 1, 1, 0, 1, 0, 10, 3, 4, 5, 0, 5, 0, 5, 6, 1, 1, 0, 0]
arg3 = []  # <type 'list'>: [0, 10, 264, 0, 264, 48, 2, 172, 216, 260, 8, 6, 0, 6, 172, -1, 264, 0, 0]
arg1Str = []  # <type 'list'>: ['', '\tR1', '\tR1', '', '\tR1', '\tR1', '\tR10', '\tR3', '\tR4', .....]
arg2Str = []  # <type 'list'>: ['', ', R0', ', 264', '', ', 264', ', #48', ', R1', ', 172', ', 216', ...]'
arg3Str = []  # <type 'list'>: ['', ', #10', '(R0)', '', '(R0)', '', ', #2', '(R10)', '(R10)', '(R0)',...]
mem = []  # <type 'list'>: [-1, -2, -3, 1, 2, 3, 0, 0, 5, -5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
binMem = []  # <type 'list'>: ['11111111111111111111111111111111', '11111111111111111111111111111110', ...] opcode = []
opcode = []
opcodeStr = []
instructions = []
instrSpaced = []
registers = []
numInstr = 0

# masks
rnMask = 0x3e0  # 1st argument ARM Rn
rmMask = 0x1F0000  # second argument ARM Rm
rdMask = 0x1F  # destination ARM Rd
imMask = 0x3FFC00  # ARM I immediate
shmtMask = 0xFC00  # ARM shamt
addrMask = 0x1FF000  # ARM address for id and st
addr2Mask = 0xFFFFE0  # addr for CB format
imsftMask = 0x600000  # shift for IM formatw
imdataMask = 0x1FFFE0  # data for IM type

# input/output file paths
input = "input"
output = "NOTWORKING"

def binToSpacedR(s):
    spaced = s[0:11] + " " + s[11:16] + " " + s[16:22] + " " + s[22: 27]
    spaced += " " + s[27:32]
    return spaced


def binToSpacedD(s):
    spaced = s[0:11] + " " + s[11:20] + " " + s[20:22] + " " + s[22:27]
    spaced += " " + s[27:32]
    return spaced

def binToSpacedI(s):
    spaced = s[0:11] + " " + s[11: 22] + " " + s[22:27] + " " + s[27:32]
    return spaced

def binToSpacedB(s):
    return s[0:6] + " " + s[6:32]

def binToSpacedCB(s):
    return s[0:8] + " " + s[8:27] + " " + s[27: 32]

def binToSpacedIM(s):
    return s[ 0:9 ] + " " + s[ 9:11 ] + " " + s[ 11:27 ] + " " + s[ 27:32 ]

def binToSpacedBreak(s):
    return s[ 0:8 ] + " " + s[ 8:11 ] + " " + s[ 11:16 ] + " " + s[ 16:21 ] + " " + s[ 21:26 ] + " " + s[ 26:32 ]

def binToSpacedInt(s):
    return s[ 0:32 ]

def binToDecimalPos(s):

    flipped = s[::-1]
    value = 0
    i = 0

    #print 'bitstring: ' + s
    #print 'flipped: ' + flipped

    for char in flipped:
       # print 'value is: ' + str(value) + ' when i is: ' + str(i)
        if (char == '1'):
            value += 2**(i)
        i += 1

    return value

def binToDecimalNeg(s):
    flipped = s[::-1]
    value = 0
    i = -1

    for char in flipped:
        if (char == '0'):
            value += 2**i
        i += 1

    value = -value - 1

    return value

class Disassembler:

    output = "NOTWORKING"

    global opcodeStr
    global arg1
    global arg2
    global arg3
    global arg1Str
    global arg2Str
    global arg3Str
    global mem
    global binMem
    global opcode
    global numInstr

    def __init__(self):
        self.setup()
        self.disassemble()
        self.formatOutput()

# gets the arguments and read in input -> stores input in instructions
    def setup(self):
        global  output
        global input
        # get file names
        for i in range(len(sys.argv)):
            if (sys.argv[i] == '-i' and i < (len(sys.argv) - 1)):
                input = sys.argv[i + 1]
            if (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
                output = sys.argv[i + 1]


        # open file for reading
        with open(input, 'r') as fin:
            for line in fin:
                instructions.append(line)

    def disassemble(self):
        i = -1
        j = -1
        broken = True

        for instr in instructions:

            i += 1

            mem.append(str(96 + (i * 4))) # memory location
            opcode.append(int(instr, base=2) >> 21)

            if( opcode[i] == 1112 ):  # if opcode = 1112 -> ADD
                opcodeStr.append("\tADD")        # R Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & rmMask) >> 16)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1624 ):           # SUB = 1624
                opcodeStr.append("\tSUB")        # R Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & rmMask) >> 16)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] >= 1160 and opcode[i] <= 1161 ):   # ADDI => 1160 - 1161
                opcodeStr.append("\tADDI")                     # I Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & imMask) >> 10)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(binToDecimalPos(instr[10:22])))

                instrSpaced.append(binToSpacedI(instr))

            elif( opcode[i] >= 1672 and opcode[i] <= 1673 ): # SUBI => 1672 - 1673
                opcodeStr.append("\tSUBI")                     # I Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & imMask) >> 10)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(binToDecimalPos(instr[10:22])))

                instrSpaced.append(binToSpacedI(instr))

            elif( opcode[i] == 1104 ): # AND => 1104
                opcodeStr.append("\tAND")  # R Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & rmMask) >> 16)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1360 ): # ORR => 1360
                opcodeStr.append("\tORR")  # R Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & rmMask) >> 16)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1872 ): # EOR => 1872
                opcodeStr.append("\tEOR")  # R TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & rmMask) >> 16)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1690 ): # LSR => 1690
                opcodeStr.append("\tLSR")  # R TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & rnMask) >> 5)  # arg1 is R1
                arg2.append((int(instr, base=2) & shmtMask) >> 10)  # arg2 is shamt
                arg3.append((int(instr, base=2) & rdMask) >> 0)  # arg3 is R0

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1691 ): # LSL => 1691
                opcodeStr.append("\tLSL")  # R TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & rnMask) >> 5)  # arg1 is R1
                arg2.append((int(instr, base=2) & shmtMask) >> 10)  # arg2 is shamt
                arg3.append((int(instr, base=2) & rdMask) >> 0)  # arg3 is R0

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1984 ): # STUR => 1984
                opcodeStr.append("\tSTUR") # D TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & rnMask) >> 5)  # R2
                arg2.append((int(instr, base=2) & rmMask) >> 12)  # address
                arg3.append((int(instr, base=2) & rdMask) >> 0)  # R1

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", [R" + str(arg1[i]))
                arg3Str.append(", #" + str(binToDecimalPos(instr[12:20])) + "]")

                instrSpaced.append(binToSpacedD(instr))

            elif( opcode[i] == 1986 ): # LDUR => 1986
                opcodeStr.append("\tLDUR") # D TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & rnMask) >> 5)  # R2
                arg2.append((int(instr, base=2) & rmMask) >> 16)  # address
                arg3.append((int(instr, base=2) & rdMask) >> 0)  # R1

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", [R" + str(arg1[i]))
                arg3Str.append(", #" + str(binToDecimalPos(instr[12:20])) + "]")

                instrSpaced.append(binToSpacedD(instr))

            elif( opcode[i] >= 160 and opcode[i] <= 191 ):  # B => 160 - 191
                opcodeStr.append("\tB") # B TYPE INSTRUCTION

                arg1.append('')
                arg2.append('')
                arg3.append('')

                arg1Str.append("\t#" + str(binToDecimalPos(instr[6:32])))
                arg2Str.append('')
                arg3Str.append('')

                instrSpaced.append(binToSpacedB(instr))

            elif( opcode[i] >= 1440 and opcode[i] <= 1447 ):  # CBZ => 1440 - 1447
                opcodeStr.append("\tCBZ") # CB TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & addr2Mask) >> 5)
                arg2.append((int(instr, base=2) & rdMask) >> 0)
                arg3.append('')

                arg1Str.append("\tR" + str(arg2[i]))
                arg2Str.append(", #" + str(arg1[i]))
                arg3Str.append('')

                instrSpaced.append(binToSpacedCB(instr))

            elif( opcode[i] >= 1448 and opcode[i] <= 1455 ):  # CBNZ => 1448 - 1455
                opcodeStr.append("\tCBNZ") # CB TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & addr2Mask) >> 5)
                arg2.append((int(instr, base=2) & rdMask) >> 0)
                arg3.append('')

                arg1Str.append("\tR" + str(arg2[i]))
                arg2Str.append(", #" + str(arg1[i]))
                arg3Str.append('')

                instrSpaced.append(binToSpacedCB(instr))

            elif( opcode[i] >= 1684 and opcode[i] <= 1687 ):
                opcodeStr.append("\tMOVZ") # IM TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & imdataMask) >> 5)
                arg2.append(16*((int(instr, base=2) & imsftMask) >> 21))
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", " + str(arg1[i]))
                arg3Str.append(", LSL " + str(arg2[i]))

                instrSpaced.append(binToSpacedIM(instr))

            elif( opcode[i] >= 1940 and opcode[i] <= 1943 ):
                opcodeStr.append("\tMOVK") # IM TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & imdataMask) >> 5)
                arg2.append(16*((int(instr, base=2) & imsftMask) >> 21))
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", " + str(arg1[i]))
                arg3Str.append(", LSL " + str(arg2[i]))

                instrSpaced.append(binToSpacedIM(instr))

            elif( opcode[i] == 2038 ): # BREAK => 2038

                self.numInstr = i

                opcodeStr.append("\tBREAK")

                arg1.append('')
                arg2.append('')
                arg3.append('')

                arg1Str.append('')
                arg2Str.append('')
                arg3Str.append('')

                instrSpaced.append(binToSpacedBreak(instr))

            elif (broken):
                j += 1
                binMem.append((int(instr, base=2) >> 31 ) & 0x1)

                if( binMem[j] == 1 ):
                    opcodeStr.append("\t" + str(binToDecimalNeg(instr)))

                elif( binMem[j] == 0 ):
                    opcodeStr.append("\t" + str(binToDecimalPos(instr)))

                arg1.append('')
                arg2.append('')
                arg3.append('')

                arg1Str.append('')
                arg2Str.append('')
                arg3Str.append('')

                instrSpaced.append(binToSpacedInt(instr))

        self.numInstr = i - j

    def formatOutput(self):
        with open(output + "_dis.txt", 'w') as myFile:
            i = 0
            for opcode in opcodeStr:
                writeData = instrSpaced[i] + "\t" + mem[i] + ' ' + opcode + arg1Str[i] + arg2Str[i] + arg3Str[i] + '\n'
                print writeData
                myFile.write(writeData)
                i += 1


class Simulator(Disassembler):

    global registers
    global numInstr
    registers = [0 for i in xrange(32)]

    def __init__(self): #override init

        #disassemble
        Disassembler.__init__(self) #super.init

        with open(output + '_sim.txt', 'w') as myFile:
            for i in range(0, self.numInstr): #loop for number of instructions

                writeData = ''

                writeData += '====================\n'
                writeData += 'cycle: ' + str(mem[i])
                writeData += '\t' + opcodeStr[i]
                writeData += '   \t' + arg1Str[i] + '\t' + arg2Str[i].replace(',','') + '\t' + arg3Str[i].replace(',','')
                writeData += '\n\nRegisters:'

                for x in range(0, 4):
                    writeData += '\nr'
                    writeData += '' if x * 8 > 9 else '0'
                    writeData += str(x * 8) + ':'
                    for y in range(0,8):
                        writeData += '\t' + str(registers[x*y])

                print writeData
                myFile.write(writeData)


if __name__ == "__main__":
    sim = Simulator()

