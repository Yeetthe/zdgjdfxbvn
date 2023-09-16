# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)
# This code has again been hoisted by the CGS Digital Innovation Department
# giving credit to the above authors for the benfit of our education in ML

import math
import random
import sys
import os

import neat
import pygame

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1920
HEIGHT = 1080
 # this is for later

CAR_SIZE_X = 50
CAR_SIZE_Y = 50

BORDER_COLOR = (255, 255, 255, 255)  # Color To Crash on Hit

current_generation = 0  # Generation counter
"""
The Car Class 

Throughout this section, you will need to explore each function
and provide extenive comments in the spaces denoted by the 
triple quotes(block quotes) """ """.
Your comments should describe each function and what it is doing, 
why it is necessary and where it is being used in the rest of the program.

"""


class Car:
    """1. This Function:
    This function is the class constructor. This is a special function which is called upon when an
    object of the car class is instantiated. Attributes of the car class are defined here.
    Notably, alive, distance, time, radars and position

    """

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load(
            "car-green.png"
        ).convert()  # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # self.position = [690, 740] # Starting Position
        self.position = [830, 920]  # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False  # Flag For Default Speed Later on

        self.center = [
            self.position[0] + CAR_SIZE_X / 2,
            self.position[1] + CAR_SIZE_Y / 2,
        ]  # Calculate Center

        self.radars = []  # List For Sensors / Radars
        self.drawing_radars = []  # Radars To Be Drawn

        self.alive = True  # Boolean To Check If Car is Crashed

        self.distance = 0  # Distance Driven
        self.time = 0  # Time Passed

    """ 2. This Function:
    this draws/renders (shows) the new position of the car on the pygame window. 
    When its called it renders the new position, rotation, and those little 
    sensor things that come off the car. the sensors/radars are optional. this is 
    a very essential function if you want to be able to see the simulation
    in a visual way.
    """

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw Sprite
        self.draw_radar(screen)  # OPTIONAL FOR SENSORS

    """ 3. This Function:
    Is the function that draws the radars of the car, which are the visualization of the data the
    car uses to 'see' its surroundings, this is optional but its useful in certain cases.
    """

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    """ 4. This Function:
    this function checks wether or not the car has collided with the barrier which 'ends' the car, it 
    senses if the coordinates of one of the corners of the car sprite has the same collor as the
    border, it ends the car. because the car has gon under the border making that coordinate
    white.
    """

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    """ 5. This Function:
    Checks the cars' radars by using cos and sin. cos and sin allows the x and y values beween 
    the car and the barrier to be calculated in order to find the hypotnuse (distance between
    car and barier in this case). i made a sin-cos visualiisation in desmos so go check that 
    out in /explanations. after that it uses a formula to find the distance between the car
    and the barier
    """

    def check_radar(self, degree, game_map):
        length = 0
        x = int(
            self.center[0]
            + math.cos(math.radians(360 - (self.angle + degree))) * length
        )
        y = int(
            self.center[1]
            + math.sin(math.radians(360 - (self.angle + degree))) * length
        )

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1
            x = int(
                self.center[0]
                + math.cos(math.radians(360 - (self.angle + degree))) * length
            )
            y = int(
                self.center[1]
                + math.sin(math.radians(360 - (self.angle + degree))) * length
            )

        # Calculate Distance To Border And Append To Radars List
        dist = int(
            math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2))
        )
        self.radars.append([(x, y), dist])

    """ 6. This Function:
    updates posision, rotation and clears the radars of the cars. it calculates:
    rotation: by using sin and cos in order to calculate the new value by using 
    the length of the car midpoint to the corner and using trig to find the new 
    position of the corners.

    position: by multiplying the speed by cosine of the angle of the car and the
    speed of the car, along with x, -x y, and -y values to move it in the right 
    direction

    radars: by simply checking if the position of a corner of a car is the same 
    color of a boundery.
    """

    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1

        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [
            int(self.position[0]) + CAR_SIZE_X / 2,
            int(self.position[1]) + CAR_SIZE_Y / 2,
        ]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X
        left_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length,
        ]
        right_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length,
        ]
        left_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length,
        ]
        right_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length,
        ]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 90): # subdivide the last number by 180 / (the numeber of radars you want) - 1
            self.check_radar(d, game_map)

    """ 7. This Function:
    gets the distance to the border of the track by calculating the radars individually
    and returning then via an array which is used to calculate the new values for the 
    next gen of cars.
    """

    def get_data(self):
        # Get Distances To Border

        radars = self.radars
        return_values = [0, 0, 0] # make sure to make the ammount of 0s the ammount of radars you want
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    """ 8. This Function:
    checks if its alive (not much else)
    """

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    """ 9. This Function:
    calculates reward by calculating distance the car travaled divided by the size
    of the car divided by 2. im not sure why you have to divide by (size / 2)
    but I think that its so it can stay within a certain parameter like 0 < distance < 1
    or somthething like this. this data is then used to figure out the best car
    and will produce cars that are like the best car.
    """

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    """ 10. This Function:
    rotates center of the car by using the angle variable we calculated earlier 
    and then applies that to the image. this is only a graphical change, and
    im not sure why we need to calculate the corner rotation as well.
    """

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


""" this func:
creates an empty collection for Nets and Cars
nets meaning a neural network that match each genome e.g. genome[0] is to nets[0]; genome[1] is to nets[1] ans so on
cars = multiple diffrent car classes at the same time, independent from one another

initiallizes the pygame window and sets the mode to fullscreen

create a neural network (NN) for each genome using neat.nn.FeedForwardNetwork.create(g, config). basically this creates a NN for the g'th 
genome in genomes and uses a config (specified when calling the function) to assign certain values to the NN. this is then appended to nets list
sets the g'th genome fitness to 0
new instance pf the class car is appended to cars list

creates clock variable to keep track of time using Clock()
selects fonts
selects map and applies the .convert() function to the map (is it a func?). since mr zampongna commented that it speeds up the simulation,
im going to assume that it converts it into int

globalizes the var current_generation and adds 1 to the current_generation var, indicating the n'th generation of the simulation

counter (idk)

loop:

if down key of esc is pressed, stop simulation and quit window

gets action from cars
 Using nets[i].activate(car.get_data()), the neural network for each automobile is activated with the sensor data from the vehicle.
The neural network output's highest value determines whether to move the car to the left, right, slow down, or accelerate.
Updating Car Movement and Fitness:



Every time a car is alive, its fitness improves and its position and movement are adjusted in accordance with what it did.



It is counted how many vehicles are still on the road.
If there are no moving vehicles, the simulation cycle is finished.

The simulation's running time is roughly constrained by a straightforward counter.

On the screen, the game's map is displayed.
all alive cars are rendered again.

The simulation's running time is roughly constrained by a straightforward counter.

Drawing the game's setting:
On the screen, the game's map is displayed.
An image of each alive car is displayed on the screen.

Information Display:
The screen shows textual data regarding the current generation, the number of active automobiles, and mean fitness.

Display and Frame Rate Updates:
The drawn elements are updated on the display.

The clock is used to regulate the frame rate, guaranteeing a maximum of 60 frames per second.

"""



def run_simulation(genomes, config):
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # Initialize PyGame And The Display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    mean_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load("map3.png").convert()  # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Exit On Quit Event
        """
        Mod: added on keydown/esc to quit the game
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10  # Left
            elif choice == 1:
                car.angle -= 10  # Right
            elif choice == 2:
                if car.speed - 2 >= 12:
                    car.speed -= 2  # Slow Down
            else:
                car.speed += 2  # Speed Up

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40:  # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
        text = generation_font.render(
            "Generation: " + str(current_generation), True, (0, 0, 0)
        )
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        text = mean_font.render(
            "Mean Fitness: " + str(neat.StatisticsReporter().get_fitness_mean()),
            True,
            (0, 0, 0),
        )
        text_rect = text.get_rect()
        text_rect.center = (900, 530)
        screen.blit(text, text_rect)

        """
        mod writes top fitness for the specified generation
        """
        # empty list for all genomes (to make it more simple)
        genomelist = []
        genomelist.append(genomes[0][1].fitness)

        if current_generation == 5: # when the 5th generation starts
            with open('results.txt', 'w') as f: # read file results.txt mode: write
                f.write('\n' + str(max(genomelist)) + '') # writes the max interger in the list therefore extracting the higest fitness
        else:
            pass

        pygame.display.flip()
        clock.tick(60)  # 60 FPS


"""
this section:

if __name__ = "__main__"
means its only executed if the file is run directly as opposed to a module

config.txt is loaded with all its information detailed with info around the NN settings
controlls input nodes, hidden layers, output nodes, number population size
and everything related to the NN

default genome dictates the mutation rate, node aggregation, node bias, and specifies the number of hidden, input, and output nodes

default reproduction dictates the number of elites (the best fitness recorded across all generations)
and survival threshhold which is the threshold of how many genomes are considered for reproduction

defaultspecies set dictates compatibility threshold which is the threshold used for determining species separation.
Genomes with compatibility distance below this threshold belong to the same species.

default stagnation dictates the fitness function which calculates the score which determines how likely a genome will be selected for reproduction.
max stagnation specifies the maximum number of generations a species can remain stagnant before it goes extinct.

species eliteism dictates the ammount of the number of elite genomes for each species
"""

if __name__ == "__main__":
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)
