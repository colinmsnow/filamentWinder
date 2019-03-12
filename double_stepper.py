#CURRENT APPLICATION INFO
#200 steps/rev
#12V, 350mA
#Big Easy driver = 1 step mode

"""
Class to drive two stepper motors for a filament winder given winding angles

"""

from time import sleep
import math
import RPi.GPIO as gpio #https://pypi.python.org/pypi/RPi.GPIO
#import exitHandler #uncomment this and line 58 if using exitHandler

class Winder:
	#instantiate stepper 
	#pins = [stepPin, directionPin, enablePin]
	def __init__(self, pins,pins2):

		self.pins = pins
		self.pins2 = pins2
		self.stepPin = self.pins[0]
		self.directionPin = self.pins[1]
		self.enablePin = self.pins[2]
		self.homePin = self.pins[3]

		self.stepPin2 = self.pins2[0]
		self.directionPin2 = self.pins2[1]
		self.enablePin2 = self.pins2[2]
		# self.homePin2 = self.pins2[3]

		self.absolute_position = 0
		self.absolute_position2 = 0

		self.pulley_diameter = .5    # change and assign units later
		
		#use the broadcom layout for the gpio
		gpio.setmode(gpio.BCM)
		
		#set gpio pins
		gpio.setup(self.stepPin, gpio.OUT)
		gpio.setup(self.directionPin, gpio.OUT)
		gpio.setup(self.enablePin, gpio.OUT)
		gpio.setup(self.homePin, gpio.IN)

		gpio.setup(self.stepPin2, gpio.OUT)
		gpio.setup(self.directionPin2, gpio.OUT)
		gpio.setup(self.enablePin2, gpio.OUT)
		
		#set enable to high (i.e. power is NOT going to the motor)
		gpio.output(self.enablePin, True)
		gpio.output(self.enablePin2, True)
		
		#print("Stepper initialized (step=" + self.stepPin + ", direction=" + self.directionPin + ", enable=" + self.enablePin  ")")
		print('winder initialized')
	

	def defineParameters(self, mandrel_length, mandrel_diameter, filament_width):
		self.mandrel_length = mandrel_length
		self.mandrel_diameter = mandrel_diameter
		self.filament_width = filament_width

		print('mandrel length:' + str(mandrel_length) + 'mandrel diameter:' + str(mandrel_diameter) + 'filament width:' + str(filament_width))


	#clears GPIO settings
	def cleanGPIO(self):
		gpio.cleanup()
	

	def wrap90(self, direction, speed=.002):
		#set enable to low (i.e. power IS going to the motor)
		gpio.output(self.enablePin, False)
		
		#set the output to true for left and false for right
		turnRight = True  # possibly messed this up by changing it from left to right
		if (direction == 'left'):
			turnRight = False
		elif (direction != 'right'):
			print("STEPPER ERROR: no direction supplied")
			return False
		gpio.output(self.directionPin, turnRight)
		gpio.output(self.directionPin2, False)   # not sure if this is the right direction

		stepCounter = 0

		steps = self.mandrel_length  # apply a constant here later to convert to inches
	
		waitTime = 0.000001/speed #waitTime controls speed


		#do the math to decide the relative speeds

		wrap_length = math.pi * self.mandrel_diameter
		mandrel_tangential_speed = (wrap_length / (self.filament_width * self.pulley_diameter)) * speed
		mandrel_rotational_speed = mandrel_tangential_speed / (self.mandrel_diameter/2)                         # left off here last time still need to implement the speed adjustments




		while stepCounter < steps:
			#gracefully exit if ctr-c is pressed
			#exitHandler.exitPoint(True) #exitHandler.exitPoint(True, cleanGPIO)

			#turning the gpio on and off tells the easy driver to take one step
			gpio.output(self.stepPin, True)
			gpio.output(self.stepPin, False)
			stepCounter += 1
			if direction == 'left':
				self.absolute_position -=1
			if direction == 'right' :
				self.absolute_position +=1
			#wait before taking the next step thus controlling rotation speed
			sleep(waitTime)
		
		if (stayOn == False):
			#set enable to high (i.e. power is NOT going to the motor)
			gpio.output(self.enablePin, True)

		print("stepperDriver complete (turned " + direction + " " + str(steps) + " steps)")

	
	#step the motor
	# steps = number of steps to take
	# direction = direction stepper will move
	# speed = defines the denominator in the waitTime equation: waitTime = 0.000001/speed. As "speed" is increased, the waitTime between steps is lowered
	# stayOn = defines whether or not stepper should stay "on" or not. If stepper will need to receive a new step command immediately, this should be set to "True." Otherwise, it should remain at "False."
	def step(self, steps, direction, speed=.005, stayOn=False):
		#set enable to low (i.e. power IS going to the motor)
		gpio.output(self.enablePin, False)
		
		#set the output to true for left and false for right
		turnRight = True  # possibly messed this up by changing it from left to right
		if (direction == 'left'):
			turnRight = False
		elif (direction != 'right'):
			print("STEPPER ERROR: no direction supplied")
			return False
		gpio.output(self.directionPin, turnRight)

		stepCounter = 0
	
		waitTime = 0.000001/speed #waitTime controls speed

		while stepCounter < steps:
			#gracefully exit if ctr-c is pressed
			#exitHandler.exitPoint(True) #exitHandler.exitPoint(True, cleanGPIO)

			#turning the gpio on and off tells the easy driver to take one step
			gpio.output(self.stepPin, True)
			gpio.output(self.stepPin, False)
			stepCounter += 1
			if direction == 'left':
				self.absolute_position -=1
			if direction == 'right' :
				self.absolute_position +=1
			#wait before taking the next step thus controlling rotation speed
			sleep(waitTime)
		
		if (stayOn == False):
			#set enable to high (i.e. power is NOT going to the motor)
			gpio.output(self.enablePin, True)

		print("stepperDriver complete (turned " + direction + " " + str(steps) + " steps)")


	

	def home(self,direction = 'left', speed=.0002, stayOn=False):
		#set enable to low (i.e. power IS going to the motor)
		gpio.output(self.enablePin, False)
		
		#set the output to true for left and false for right
		turnLeft = True
		if (direction == 'left'):
			turnRight = False;
		elif (direction != 'right'):
			print("STEPPER ERROR: no direction supplied")
			return False
		gpio.output(self.directionPin, turnRight)

	
		waitTime = 0.000001/speed #waitTime controls speed
		homed = gpio.input(self.homePin)
		print(homed)
		while gpio.input(self.homePin) == 0:
			#gracefully exit if ctr-c is pressed
			#exitHandler.exitPoint(True) #exitHandler.exitPoint(True, cleanGPIO)

			#turning the gpio on and off tells the easy driver to take one step
			gpio.output(self.stepPin, True)
			gpio.output(self.stepPin, False)
 
			#wait before taking the next step thus controlling rotation speed
			sleep(waitTime)
		self.absolute_position = 0
		if (stayOn == False):
			#set enable to high (i.e. power is NOT going to the motor)
			gpio.output(self.enablePin, True)
		print("stepperDriver homed successfully")

	def go_to(self, position, speed=.005, stayOn=False):
		#set enable to low (i.e. power IS going to the motor)
		gpio.output(self.enablePin, False)
		
		#set the output to true for left and false for right
		if self.absolute_position > position :
			turnRight = False
		if self.absolute_position < position:
			turnRight = True
		else:
			turnRight = False

		gpio.output(self.directionPin, turnRight)

		stepCounter = 0
	
		waitTime = 0.000001/speed #waitTime controls speed

		while stepCounter < abs(position-self.absolute_position):
			#gracefully exit if ctr-c is pressed
			#exitHandler.exitPoint(True) #exitHandler.exitPoint(True, cleanGPIO)

			#turning the gpio on and off tells the easy driver to take one step
			gpio.output(self.stepPin, True)
			gpio.output(self.stepPin, False)
			stepCounter += 1
			#wait before taking the next step thus controlling rotation speed
			sleep(waitTime)
		self.absolute_position = position
		if (stayOn == False):
			#set enable to high (i.e. power is NOT going to the motor)
			gpio.output(self.enablePin, True)

		print("stepperDriver moved to absolute position " + str(self.absolute_position) )


		
testStepper = Winder([23,24,25,22])
#testStepper.step(1,'left',stayOn = False )
testStepper.home()
testStepper.go_to(3000)
testStepper.go_to(1000)
testStepper.go_to(3000)
testStepper.go_to(1000)
testStepper.cleanGPIO()