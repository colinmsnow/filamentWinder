# Filament Winder
Experimental code to creata a filament winding machine with two axes

Filament winding is the process of wrapping a long strand, or filament, of some fiber material (Usually carbon, fiberglass, or kevlar) around some form while combining it with an epoxy to create a part which is the shape of whatever form it is wound about. This method allows the angle and position of the fibers to be calculated and optimized by directing more fibers in the directions where more strength is needed. This produces higher quality parts which are lighter, stronger, and cheaper than traditional methods where cloth sheets are used.

The machine is controlled with two servo motors which are attached to a Raspberry Pi. The Pi does all of the computation to determine the servo movements based on the given layers and then executes these actions by running the motors simultaneously. The discrete stepping of the servos makes the system very exact and allows it to wind precisely without zeroing the axes or using any corrective methods. 

This code should work with any stepper drivers with a direction pin and a step pin. The GPIO pins for each of these can be adjusted and are set by default to use most of the available pins on the old-style Raspberry Pi.

This code takes a user input in the form of the parameters of the machine and the layers it needs to execute. First set up the global variables of steps per revolution, gear ratios, and pulley diameters, then the variables in the Winder class of the mandrel length, mandrel diameter, and filament width.

The layers consist of angle and speed arguments given to the winder in the form of testStepper.wrap(direction, angle). the direction is in degrees from horizontal. There is a separate function for wrapping near 90 degrees which uses the filament's width to determine the offset and thus creates a perfect wrap with no gaps.
