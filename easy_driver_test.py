#CURRENT APPLICATION INFO
#200 steps/rev
#12V, 350mA
#Big Easy driver = 1/16 microstep mode
#Turn a 200 step motor left one full revolution: 3200

from time import sleep
import RPi.GPIO as gpio #https://pypi.python.org/pypi/RPi.GPIO
#import exitHandler #uncomment this and line 58 if using exitHandler

class Stepper:
	#instantiate stepper 
	#pins = [stepPin, directionectionPin, enablePin]
	def __init__(self, pins):
		#setup pins
		self.pins = pins
		self.stepPin = self.pins[0]
		self.directionectionPin = self.pins[1]
		self.enablePin = self.pins[2]
		self.homePin = self.pins[3]
		self.absolute_position = 0
		
		#use the broadcom layout for the gpio
		gpio.setmode(gpio.BCM)
		
		#set gpio pins
		gpio.setup(self.stepPin, gpio.OUT)
		gpio.setup(self.directionectionPin, gpio.OUT)
		gpio.setup(self.enablePin, gpio.OUT)
		gpio.setup(self.homePin, gpio.IN)
		
		#set enable to high (i.e. power is NOT going to the motor)
		gpio.output(self.enablePin, True)
		
		#print("Stepper initialized (step=" + self.stepPin + ", directionection=" + self.directionectionPin + ", enable=" + self.enablePin  ")")
		print('stepper initialized')
	
	#clears GPIO settings
	def cleanGPIO(self):
		gpio.cleanup()
	
	#step the motor
	# steps = number of steps to take
	# direction = directionection stepper will move
	# speed = defines the denominator in the waitTime equation: waitTime = 0.000001/speed. As "speed" is increased, the waitTime between steps is lowered
	# stayOn = defines whether or not stepper should stay "on" or not. If stepper will need to receive a new step command immediately, this should be set to "True." Otherwise, it should remain at "False."
	def step(self, steps, direction, speed=.005, stayOn=False):
		#set enable to low (i.e. power IS going to the motor)
		gpio.output(self.enablePin, False)
		
		#set the output to true for left and false for right
		turnLeft = True
		if (direction == 'left'):
			turnRight = False;
		elif (direction != 'right'):
			print("STEPPER ERROR: no directionection supplied")
			return False
		gpio.output(self.directionectionPin, turnRight)

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
			print("STEPPER ERROR: no directionection supplied")
			return False
		gpio.output(self.directionectionPin, turnRight)

	
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

		gpio.output(self.directionectionPin, turnRight)

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


		
testStepper = Stepper([23,24,25,22])
#testStepper.step(1,'left',stayOn = False )
testStepper.home()
testStepper.go_to(3000)
testStepper.go_to(1000)
testStepper.go_to(3000)
testStepper.go_to(1000)
testStepper.cleanGPIO()
