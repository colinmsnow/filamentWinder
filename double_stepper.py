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
import threading
#import exitHandler #uncomment this and line 58 if using exitHandler


### GLOBALS ###
### All lengths in mm ###

STEPS_PER_REV = 200
MANDREL_GEAR_RATIO = 2.3333
BELT_PULLEY_DIAMETER = 15





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
	

	def wrap90(self, direction, speed=.01, stayOn = False):
		#set enable to low (i.e. power IS going to the motor)
		gpio.output(self.enablePin, False)
		gpio.output(self.enablePin2, False)
		
		#set the output to true for left and false for right
		turnRight = True  # possibly messed this up by changing it from left to right
		if (direction == 'left'):
			turnRight = False
		elif (direction != 'right'):
			print("STEPPER ERROR: no direction supplied")
			return False
		gpio.output(self.directionPin, turnRight)
		gpio.output(self.directionPin2, False)   # not sure if this is the right direction


		
	
	


		#do the math to decide the relative speeds


		# tangential = r * rotational

		mandrel_circumference = math.pi * self.mandrel_diameter


		mandrel_distance_per_revolution = mandrel_circumference / MANDREL_GEAR_RATIO
		mandrel_distance_per_step = mandrel_distance_per_revolution / STEPS_PER_REV

		carrage_distance_per_revolution = math.pi* BELT_PULLEY_DIAMETER
		carrage_distance_per_step = carrage_distance_per_revolution / STEPS_PER_REV 

		relative_distance = (self.filament_width / mandrel_circumference) 
		relative_steps = relative_distance * (carrage_distance_per_step / mandrel_distance_per_step)



		mandrel_speed = speed

		carrage_speed = mandrel_speed * relative_steps


		carraige_steps = self.mandrel_length / carrage_distance_per_step

		mandrel_steps = carraige_steps / relative_steps


		print('Linear speed is ' + str(carrage_speed))
		print('Rotational speed is ' + str(mandrel_speed))

		a = threading.Thread(target = self.step, args=(carraige_steps, turnRight,self.enablePin, self.stepPin, self.directionPin, carrage_speed ))
		b = threading.Thread(target = self.step, args=(mandrel_steps, False,self.enablePin2, self.stepPin2, self.directionPin2, mandrel_speed))   # check if it is the right direction

		a.start()
		b.start()

		a.join()
		b.join()
		

		print("90 degree wind complete")

	def wrap(self, direction, angle, speed=.07, stayOn = False):

		# testStepper.home()  # homing in the beginning may or may not be a good idea

		# stepsperinch = 30  # random guess check later
		# stepsperrotation = 200  # also a guess



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



		mandrel_circumference = math.pi * self.mandrel_diameter


		mandrel_distance_per_revolution = mandrel_circumference / MANDREL_GEAR_RATIO
		mandrel_distance_per_step = mandrel_distance_per_revolution / STEPS_PER_REV

		carrage_distance_per_revolution = math.pi* BELT_PULLEY_DIAMETER
		carrage_distance_per_step = carrage_distance_per_revolution / STEPS_PER_REV 

		# relative_distance = math.sin(math.radians(90-angle))
		# relative_steps = relative_distance * (carrage_distance_per_step / mandrel_distance_per_step)


		# Use tan instead of sin to get full range from 0 to infinity
		relative_distance = math.tan(math.radians(angle))
		relative_steps =  (carrage_distance_per_step / mandrel_distance_per_step) / relative_distance


		mandrel_speed = speed

		carraige_speed = mandrel_speed * relative_steps


		carraige_steps = self.mandrel_length / carrage_distance_per_step

		mandrel_steps = carraige_steps / relative_steps


		print(mandrel_circumference)
		print(self.filament_width)
		print(math.cos(angle))
		number_of_passes = int((mandrel_circumference / self.filament_width) * math.cos(math.radians(angle)))

		steps_per_turn = STEPS_PER_REV * MANDREL_GEAR_RATIO

		

		mandrel_turn = int(  abs(steps_per_turn / 2 )+ abs(self.filament_width / math.sin(math.radians(angle)) )/ mandrel_distance_per_step)
		print('mandrel turn is : ' + str(mandrel_turn))




		print(' beginning wrap')
		print(' Linear speed is ' + str(carraige_speed))
		print(' Rotational speed is ' + str(mandrel_speed))
		print(' Number of passes is ' + str(number_of_passes))




		for i in range(abs(number_of_passes) * 2):

			gpio.output(self.directionPin, turnRight)
			print('turnRight = ' + str(turnRight))
			

			a = threading.Thread(target = self.step, args=(carraige_steps, turnRight,self.enablePin, self.stepPin, self.directionPin, carraige_speed ))
			b = threading.Thread(target = self.step, args=(abs(mandrel_steps), False,self.enablePin2, self.stepPin2, self.directionPin2, abs(mandrel_speed) ) )# check if it is the right direction
			

			if turnRight == True:
				turnRight = False
			else:
				turnRight = True

			a.start()
			b.start()

			a.join()
			b.join()
			print('finished synchronization')

			sleep(.25)


			
			self.step(mandrel_turn, False,self.enablePin2, self.stepPin2, self.directionPin2, abs(mandrel_speed) )

			sleep(.25)
			print('finished pass')


		

		print(str(angle) + " degree wind complete")

	
	#step the motor
	# steps = number of steps to take
	# direction = direction stepper will move
	# speed = defines the denominator in the waitTime equation: waitTime = 0.000001/speed. As "speed" is increased, the waitTime between steps is lowered
	# stayOn = defines whether or not stepper should stay "on" or not. If stepper will need to receive a new step command immediately, this should be set to "True." Otherwise, it should remain at "False."
	def step(self, steps, direction, enablePin, stepPin,directionPin, speed=.005, stayOn=False):

		#set enable to low (i.e. power IS going to the motor)
		gpio.output(enablePin, False)
		
		#set the output to true for left and false for right
		turnRight = True  # possibly messed this up by changing it from left to right
		if (direction == 'left') or direction == False:
			turnRight = False
			
		gpio.output(directionPin, turnRight)

		stepCounter = 0
	
		waitTime = 0.00015/speed #waitTime controls speed

		print('steps = ' + str(steps))

		for i in range(int(steps)):

			#gracefully exit if ctr-c is pressed
			#exitHandler.exitPoint(True) #exitHandler.exitPoint(True, cleanGPIO)

			#turning the gpio on and off tells the easy driver to take one step
			gpio.output(stepPin, True)
			gpio.output(stepPin, False)
			stepCounter += 1


			sleep(abs(waitTime))
		
		if (stayOn == False):
			#set enable to high (i.e. power is NOT going to the motor)
			gpio.output(enablePin, True)

		print("stepperDriver complete (turned " + str(direction) + " " + str(steps) + " steps)")


	

	def home(self,direction = 'left', speed=.0002, stayOn=False):
		#set enable to low (i.e. power IS going to the motor)
		gpio.output(self.enablePin, False)
		
		#set the output to true for left and false for right
		turnLeft = True
		if (direction == 'left'):
			turnRight = False
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

		self.step(20, True,self.enablePin, self.stepPin, self.directionPin  )


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


if __name__ == "__main__":
		
	#testStepper.step(1,'left',stayOn = False )
	testStepper = Winder([23, 24, 25, 22],[17, 27, 18, 10])
	testStepper.defineParameters(125,38,1.88)

	testStepper.home()
	# testStepper.wrap90('right')

	testStepper.wrap('right', 45)

	testStepper.cleanGPIO()