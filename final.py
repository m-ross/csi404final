# SUNY Albany
# Copyright (C) 2016. All rights reserved.
#
# Author: Yueming Yang
# 
# Additions and changes made by: Marcus Ross

class Circuit(object):
	def __init__(self, in1, in2):
		self.in1 = in1
		self.in2 = in2

class AndGate(Circuit):
	def circFunc(self):
		return self.in1 and self.in2

class AndGate3In(Circuit):
	def __init__(self, in1, in2, in3):
		self.in1 = in1
		self.in2 = in2
		self.in3 = in3

	def circFunc(self):
		return self.in1 and self.in2 and self.in3

class AndGate5In(Circuit):
	def __init__(self, in1, in2, in3, in4, in5):
		self.in1 = in1
		self.in2 = in2
		self.in3 = in3
		self.in4 = in4
		self.in5 = in5

	def circFunc(self):
		return self.in1 and self.in2 and self.in3 and self.in4 and self.in5

class AndGate6In(Circuit):
	def __init__(self, in1, in2, in3, in4, in5, in6):
		self.in1 = in1
		self.in2 = in2
		self.in3 = in3
		self.in4 = in4
		self.in5 = in5
		self.in6 = in6

	def circFunc(self):
		return self.in1 and self.in2 and self.in3 and self.in4 and self.in5 and self.in6

class OrGate(Circuit):
	def circFunc(self):
		return self.in1 or self.in2

class OrGate3In(Circuit):
	def __init__(self, in1, in2, in3):
		self.in1 = in1
		self.in2 = in2
		self.in3 = in3

	def circFunc(self):
		return self.in1 or self.in2 or self.in3

class OrGate4In(Circuit):
	def __init__(self, in1, in2, in3, in4):
		self.in1 = in1
		self.in2 = in2
		self.in3 = in3
		self.in4 = in4

	def circFunc(self):
		return self.in1 or self.in2 or self.in3 or self.in4

class NotGate(Circuit):
	def __init__(self, in1):
		self.in1 = in1

	def circFunc(self):
		return not self.in1

class Mux2To1(Circuit):
	def __init__(self, in1, in2, ctr1):
		self.in1 = in1
		self.in2 = in2
		self.ctr1 = ctr1

	def circFunc(self):
		ctrInvert = NotGate(self.ctr1).circFunc()
		and1 = AndGate(self.in1, ctrInvert).circFunc()
		and2 = AndGate(self.in2, self.ctr1).circFunc()
		or1 = OrGate(and1, and2)

		return or1.circFunc()

class Mux4To1(Circuit):
	def __init__(self, in1, in2, in3, in4, ctr0, ctr1):
		self.in1 = in1
		self.in2 = in2
		self.in3 = in3
		self.in4 = in4
		self.ctr0 = ctr0
		self.ctr1 = ctr1

	def circFunc(self):
		mux1 = Mux2To1(self.in1, self.in2, self.ctr1).circFunc()
		mux2 = Mux2To1(self.in3, self.in4, self.ctr1).circFunc()
		mux3 = Mux2To1(mux1, mux2, self.ctr0).circFunc()

		return mux3

class Adder(Circuit):
	def __init__(self, in1, in2, cIn):
		self.in1 = in1
		self.in2 = in2
		self.cIn = cIn

	def circFunc(self):
		and1 = AndGate(self.in1, self.cIn).circFunc()
		and2 = AndGate(self.in2, self.cIn).circFunc()
		and3 = AndGate(self.in1, self.in2).circFunc()

		cOut = OrGate3In(and1, and2, and3).circFunc()

		in1Invert = NotGate(self.in1).circFunc()
		in2Invert = NotGate(self.in2).circFunc()
		cInInvert = NotGate(self.cIn).circFunc()

		and3In1 = AndGate3In(in1Invert, in2Invert, self.cIn).circFunc()
		and3In2 = AndGate3In(in1Invert, self.in2, cInInvert).circFunc()
		and3In3 = AndGate3In(self.in1, self.in2, self.cIn).circFunc()
		and3In4 = AndGate3In(self.in1, in2Invert, cInInvert).circFunc()

		sum = OrGate4In(and3In1, and3In2, and3In3, and3In4).circFunc()

		return sum, cOut



class ALU1Bit(Circuit):
	def __init__(self, in1, in2, cIn, ctr):
		self.in1 = in1 # first operand
		self.in2 = in2 # second operand
		self.cIn = cIn # carry in
		self.ctr = ctr # control signals
		
	def circFunc(self):
		mux1 = Mux2To1(self.in1, NotGate(self.in1).circFunc(), self.ctr[0]).circFunc() # choose between A and not A; ctr[0] == AInvert
		mux2 = Mux2To1(self.in2, NotGate(self.in2).circFunc(), self.ctr[1]).circFunc() # choose between B and not B; ctr[1] == BInvert
		and1 = AndGate(mux1, mux2).circFunc() # A & B
		or1 = OrGate(mux1, mux2).circFunc() # A | B
		sumAdder, cOutAdder = Adder(mux1, mux2, self.cIn).circFunc() # A +- B
		out = Mux4To1(and1, or1, sumAdder, 0, self.ctr[2], self.ctr[3]).circFunc() # choose between and, or, add, sub; ctr[2] == output from ALU control; ctr[3] == output from ALU control
		
		return out, cOutAdder

class ALU32Bit(object):
	def __init__(self, in1, in2, cIn, ctr):
		self.in1 = in1 # first operand
		self.in2 = in2 # second operand
		self.cIn = cIn # carry in = 1 when subtracting
		self.ctr = ctr # signals from ALU Control

	def circFunc(self):
		sum = [0] * 32
		cOut = [0] * 32

		for i in range(31, -1, -1):
			if i == 31:
				cIn = self.cIn
				sumTemp, cOutTemp = ALU1Bit(self.in1[i], self.in2[i], cIn, self.ctr).circFunc()
			else:
				cIn = cOut[i + 1]
				sumTemp, cOutTemp = ALU1Bit(self.in1[i], self.in2[i], cIn, self.ctr).circFunc()

			sum[i] = sumTemp
			cOut[i] = cOutTemp

		return sum, cOut[0]

class ALUCtr(Circuit):
	def __init__(self, op1, op0, f5, f4, f3, f2, f1, f0):
		self.op1 = op1
		self.op0 = op0
		self.f5 = f5
		self.f4 = f4
		self.f3 = f3
		self.f2 = f2
		self.f1 = f1
		self.f0 = f0

	def circFunc(self):
		ctr = [0] * 4
		ctr[0] = AndGate(self.op0, NotGate(self.op0).circFunc()).circFunc()
		ctr[1] = OrGate(AndGate(NotGate(self.op1).circFunc(), self.op0).circFunc(), AndGate(self.op1, self.f1).circFunc()).circFunc()
		ctr[2] = OrGate(NotGate(self.op1).circFunc(), NotGate(self.f2).circFunc()).circFunc()
		ctr[3] = AndGate(self.op1, OrGate(self.f3, self.f0).circFunc()).circFunc()

		return ctr

class RegisterFile(Circuit):
	def __init__(self, regInitValue):
		self.registers = [0] * 32
		
		for i in range(0, 31):
				self.registers[i] = regInitValue

	def setRegValue(self, regNumDecoded, newValue):
		newValueBin = [0] * 32
		boolToBin(newValue, newValueBin) # avoid having any 'true's and 'false's in registers
		
		for i in range(0, 31):
			if regNumDecoded[i]:
				self.registers[i] = newValueBin

	def getReg(self, regNumDecoded):
		for i in range(0, 31):
			if regNumDecoded[i]:
				regValue = self.registers[i]
				
		return regValue

	def getAllReg(self):
		return self.registers

class Decoder(Circuit):
	def __init__(self, regNum):
		self.regNum = regNum

	def circFunc(self):
		regNumDecoded = [0] * 32
		regNumInvert = [0] * 5
		
		for i in range(0, 5):
			regNumInvert[i] = NotGate(self.regNum[i]).circFunc()

		regNumDecoded[0]  = AndGate5In(regNumInvert[0], regNumInvert[1], regNumInvert[2], regNumInvert[3], regNumInvert[4]).circFunc()
		regNumDecoded[1]  = AndGate5In(regNumInvert[0], regNumInvert[1], regNumInvert[2], regNumInvert[3], self.regNum[4]).circFunc()
		regNumDecoded[2]  = AndGate5In(regNumInvert[0], regNumInvert[1], regNumInvert[2], self.regNum[3], regNumInvert[4]).circFunc()
		regNumDecoded[3]  = AndGate5In(regNumInvert[0], regNumInvert[1], regNumInvert[2], self.regNum[3], self.regNum[4]).circFunc()
		regNumDecoded[4]  = AndGate5In(regNumInvert[0], regNumInvert[1], self.regNum[2], regNumInvert[3], regNumInvert[4]).circFunc()
		regNumDecoded[5]  = AndGate5In(regNumInvert[0], regNumInvert[1], self.regNum[2], regNumInvert[3], self.regNum[4]).circFunc()
		regNumDecoded[6]  = AndGate5In(regNumInvert[0], regNumInvert[1], self.regNum[2], self.regNum[3], regNumInvert[4]).circFunc()
		regNumDecoded[7]  = AndGate5In(regNumInvert[0], regNumInvert[1], self.regNum[2], self.regNum[3], self.regNum[4]).circFunc()
		regNumDecoded[8]  = AndGate5In(regNumInvert[0], self.regNum[1], regNumInvert[2], regNumInvert[3], regNumInvert[4]).circFunc()
		regNumDecoded[9]  = AndGate5In(regNumInvert[0], self.regNum[1], regNumInvert[2], regNumInvert[3], self.regNum[4]).circFunc()
		regNumDecoded[10] = AndGate5In(regNumInvert[0], self.regNum[1], regNumInvert[2], self.regNum[3], regNumInvert[4]).circFunc()
		regNumDecoded[11] = AndGate5In(regNumInvert[0], self.regNum[1], regNumInvert[2], self.regNum[3], self.regNum[4]).circFunc()
		regNumDecoded[12] = AndGate5In(regNumInvert[0], self.regNum[1], self.regNum[2], regNumInvert[3], regNumInvert[4]).circFunc()
		regNumDecoded[13] = AndGate5In(regNumInvert[0], self.regNum[1], self.regNum[2], regNumInvert[3], self.regNum[4]).circFunc()
		regNumDecoded[14] = AndGate5In(regNumInvert[0], self.regNum[1], self.regNum[2], self.regNum[3], regNumInvert[4]).circFunc()
		regNumDecoded[15] = AndGate5In(regNumInvert[0], self.regNum[1], self.regNum[2], self.regNum[3], self.regNum[4]).circFunc()
		regNumDecoded[16] = AndGate5In(self.regNum[0], regNumInvert[1], regNumInvert[2], regNumInvert[3], regNumInvert[4]).circFunc()
		regNumDecoded[17] = AndGate5In(self.regNum[0], regNumInvert[1], regNumInvert[2], regNumInvert[3], self.regNum[4]).circFunc()
		regNumDecoded[18] = AndGate5In(self.regNum[0], regNumInvert[1], regNumInvert[2], self.regNum[3], regNumInvert[4]).circFunc()
		regNumDecoded[19] = AndGate5In(self.regNum[0], regNumInvert[1], regNumInvert[2], self.regNum[3], self.regNum[4]).circFunc()
		regNumDecoded[20] = AndGate5In(self.regNum[0], regNumInvert[1], self.regNum[2], regNumInvert[3], regNumInvert[4]).circFunc()
		regNumDecoded[21] = AndGate5In(self.regNum[0], regNumInvert[1], self.regNum[2], regNumInvert[3], self.regNum[4]).circFunc()
		regNumDecoded[22] = AndGate5In(self.regNum[0], regNumInvert[1], self.regNum[2], self.regNum[3], regNumInvert[4]).circFunc()
		regNumDecoded[23] = AndGate5In(self.regNum[0], regNumInvert[1], self.regNum[2], self.regNum[3], self.regNum[4]).circFunc()
		regNumDecoded[24] = AndGate5In(self.regNum[0], self.regNum[1], regNumInvert[2], regNumInvert[3], regNumInvert[4]).circFunc()
		regNumDecoded[25] = AndGate5In(self.regNum[0], self.regNum[1], regNumInvert[2], regNumInvert[3], self.regNum[4]).circFunc()
		regNumDecoded[26] = AndGate5In(self.regNum[0], self.regNum[1], regNumInvert[2], self.regNum[3], regNumInvert[4]).circFunc()
		regNumDecoded[27] = AndGate5In(self.regNum[0], self.regNum[1], regNumInvert[2], self.regNum[3], self.regNum[4]).circFunc()
		regNumDecoded[28] = AndGate5In(self.regNum[0], self.regNum[1], self.regNum[2], regNumInvert[3], regNumInvert[4]).circFunc()
		regNumDecoded[29] = AndGate5In(self.regNum[0], self.regNum[1], self.regNum[2], regNumInvert[3], self.regNum[4]).circFunc()
		regNumDecoded[30] = AndGate5In(self.regNum[0], self.regNum[1], self.regNum[2], self.regNum[3], regNumInvert[4]).circFunc()
		regNumDecoded[31] = AndGate5In(self.regNum[0], self.regNum[1], self.regNum[2], self.regNum[3], self.regNum[4]).circFunc()

		return regNumDecoded

class MainCtr(Circuit):
	def __init__(self, op5, op4, op3, op2, op1, op0):
		self.op5 = op5
		self.op4 = op4
		self.op3 = op3
		self.op2 = op2
		self.op1 = op1
		self.op0 = op0

	def circFunc(self):
		and1 = AndGate6In(NotGate(self.op5).circFunc(), NotGate(self.op4).circFunc(), NotGate(self.op3).circFunc(), NotGate(self.op2).circFunc(), NotGate(self.op1).circFunc(), NotGate(self.op0).circFunc()).circFunc()
		and2 = AndGate6In(self.op5, NotGate(self.op4).circFunc(), NotGate(self.op3).circFunc(), NotGate(self.op2).circFunc(), self.op1, self.op0).circFunc()
		and3 = AndGate6In(self.op5, NotGate(self.op4).circFunc(), self.op3, NotGate(self.op2).circFunc(), self.op1, self.op0).circFunc()
		and4 = AndGate6In(NotGate(self.op5).circFunc(), NotGate(self.op4).circFunc(), self.op3, NotGate(self.op2).circFunc(), NotGate(self.op1).circFunc(), NotGate(self.op0).circFunc()).circFunc()

		o_RegDst = and1
		o_AluSrc = OrGate(and2, and3).circFunc()
		o_MemToReg = and2
		o_RegWrite = OrGate(and1, and2).circFunc()
		o_MemRead = and2
		o_MemWrite = and3
		o_Branch = and4
		o_ALUOp1 = and1
		o_ALUOp0 = and4

		return o_RegDst, o_AluSrc, o_MemToReg, o_RegWrite, o_MemRead, o_MemWrite, o_Branch, o_ALUOp1, o_ALUOp0


class simpleMIPS(Circuit):
	def __init__(self, instruction, registers):
	
		self.inst = instruction
		self.registers = registers

	def circFunc(self):
		mainCtr = MainCtr(self.inst[0], self.inst[1], self.inst[2], self.inst[3], self.inst[4], self.inst[5]).circFunc() # send left-most 6 bits of instruction to Control
		aluCtr = ALUCtr(mainCtr[7], mainCtr[8], self.inst[26], self.inst[27], self.inst[28], self.inst[29], self.inst[30], self.inst[31]).circFunc() # send ALUOp control signal and function code to ALU Control
		
		regSrcNum = [self.inst[6], self.inst[7], self.inst[8], self.inst[9], self.inst[10]] # 'extract' rs from the instruction
		regSrcNumDecode = Decoder(regSrcNum).circFunc() # decode the address given for rs
		regSrc = self.registers.getReg(regSrcNumDecode) # get the value at rs
		
		regTrgtNum = [self.inst[11], self.inst[12], self.inst[13], self.inst[14], self.inst[15]] # 'extract' rt from the instruction
		regTrgtNumDecode = Decoder(regTrgtNum).circFunc() # decode the address given for rt
		regTrgt = self.registers.getReg(regTrgtNumDecode) # get the value at rt
		
		regDestNum = [self.inst[16], self.inst[17], self.inst[18], self.inst[19], self.inst[20]] # 'extract' rd from the instruction
		# muxWriteRegNum = Mux2To1(regTrgtNum, regDestNum, mainCtr[0]).circFunc() # not needed for any required operations (and doesn't work anyway with current mux implementation)
		regDestNumDecode = Decoder(regDestNum).circFunc() # decode the address given for rd
		
		# signExtImm16Bits = [self.inst[16], self.inst[17], self.inst[18], self.inst[19], self.inst[20], self.inst[21], self.inst[22], self.inst[23], self.inst[24], self.inst[25], self.inst[26], self.inst[27], self.inst[28], self.inst[29], self.inst[30], self.inst[31]] # not required
		# signExtImm = signExtend16To32(signExtImm16Bits) # not required
		# muxALUSrc = Mux2To1(regTrgt, signExtImm, mainCtr[1]) # not needed for any required operations (and doesn't work anyway with current mux implementation)
		
		result, cOut = ALU32Bit(regSrc, regTrgt, aluCtr[1], aluCtr).circFunc() # send value at rs, value at rt, and ALU control signals to 32 bit ALU
		self.registers.setRegValue(regDestNumDecode, result) # update the value at rd with the ALU's output

def signExtend16To32(halfword): # unused
	word = [0] * 32
	for i in range(0, 15):
		word[i] = halfword[i]
	return word
		
def stringToBin(binIn, binOut): # input is length 32 string of '1's and '0's; output is a length 32 array of 1s and 0s
	for i in range(0, len(binIn)):
		if (binIn[i] == '1'):
			binOut[i] = 1
		else:
			binOut[i] = 0

def boolToBin(boolIn, binOut): # input is a length 32 array of True/'1's and False/'0's; output is a length 32 array of 1s and 0s
	for i in range(0, len(boolIn)):
		if (boolIn[i]):
			binOut[i] = 1
		else:
			binOut[i] = 0

def main():
	instruction = [0] * 32
	instructionString = raw_input("Enter a 32 bit instruction: ")
	# instructionString = "00000000110001110100011111100000" # default example of R[8]=R[6]+R[7]
	# print "Instruction:", instructionString, "\n" # redundant while default example not being used
	stringToBin(instructionString, instruction)

	regInitValue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0] # initial value in registers = 2
	regFile = RegisterFile(regInitValue) # initialise all registers
	
	simpleMIPSCPU = simpleMIPS(instruction, regFile).circFunc() # run the instruction
	
	allRegisters = regFile.getAllReg() # get the new value(s) in the registers
	print "\nRegisters after instruction:"
	for i in range(0, 31):
		print allRegisters[i]

if __name__ == '__main__':
	main()
