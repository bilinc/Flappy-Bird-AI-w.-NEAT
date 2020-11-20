import pygame
import neat
import time
import os
import random
pygame.font.init()

# Constants for window size
WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 0

# Load images for game
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


# Create class for game objects
class Bird(object):
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25
	ROT_VEL = 20
	ANIMATION_TIME = 5

	def __init__(self, x, y):
		self.x = x
		self.y = y
		
		self.tilt = 0	# How much the screen is tilting
		self.tick_count = 0
		self.vel = 0
		self.height = self.y

		self.img_count = 0	# which image of the bird that is currently showing
		self.img = self.IMGS[0]

	def get(self, var):
		
		if var == "x":
			return self.x
		elif var == "y":
			return self.y


	def jump(self):
		self.vel = -10.5	# velocity of the bird going up
		self.tick_count = 0	# reset tick count when jumping
		self.height = self.y

	def move(self):
		self.tick_count += 1

		d = self.vel*self.tick_count + 1.5*self.tick_count**2

		if d >= 16:
			# set a terminal velocity when moving down
			d = 16

		if d < 0:
			d -= 2

		# update current y position
		self.y = self.y + d

		# keep the bird tilting upwards
		if d < 0 or self.y < self.height + 50:
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		# tilt the bird downwards
		else:
			if self.tilt > -90:
				# make it nose dive more and more
				self.tilt -= self.ROT_VEL

	def draw(self, win):
		# Draw the game window
		self.img_count += 1

		# update the image of the bird as animation time progresses
		if self.img_count < self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0

		# when bird is pointing downwards, don't animate wing flapping
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2

		# rotate the image around the center
		rotated_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(rotated_image, new_rect.topleft)
		
	def get_mask(self):
		return pygame.mask.from_surface(self.img)


class Pipe:
	GAP = 200
	VEL = 5

	def __init__(self, x):
		self.x = x
		self.height = 0

		self.top = 0		# where top of pipe is drawn
		self.bottom = 0		# where bottom of pipe is drawn

		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)		# flip image for the pipe on the top
		self.PIPE_BOTTOM = PIPE_IMG

		# used for collision detection
		self.passed = False

		self.set_height()

	def get(self, var):
		if var == "x":
			return self.x

	def get_passed(self):
		return self.passed

	def set_passed(self, passed):
		self.passed = passed

	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM , (self.x, self.bottom))

	def collide(self, bird):
		# using mask to detect collision
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, int(self.top - round(bird.y)))
		bottom_offset = (self.x - bird.x, int(self.bottom - round(bird.y)))

		# finding point of collision
		# how far away is the bird mask from the bottom of the pipe using the bottom offset
		b_point = bird_mask.overlap(bottom_mask, bottom_offset)		# returns None if they are not colliding

		t_point = bird_mask.overlap(top_mask, top_offset)			# returns None if they are not colliding

		if t_point or b_point:
			return True

		return False


class Base:
	VEL = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		# Use two identical base images to simulate constant movement
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		# cycle image to the back after it's outside the window
		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))

		

def draw_window(win, birds, pipes, base, score, gen):
	# draw in the window at the top left position
	win.blit(BG_IMG, (0,0))
	
	# pipes comes as a list
	for pipe in pipes:
		pipe.draw(win)

	base.draw(win)

	for bird in birds:
		bird.draw(win)

	# score
	score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
	win.blit(score_label, (WIN_WIDTH - 10 - score_label.get_width(), 10))

	# generation
	gen_label = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
	win.blit(gen_label, (10, 10))

	pygame.display.update()


def eval_genomes(genomes, config):
	# Our fitness function

	global GEN
	GEN += 1

	nets = []
	ge = []
	birds = []

	for _, g in genomes:	# genomes is a tuple (id, genome_object)
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(230, 350))
		g.fitness = 0
		ge.append(g)



	base = Base(730)
	pipes = [Pipe(600)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	
	clock = pygame.time.Clock()

	score = 0

	run = True
	while run:
		clock.tick(30)	# animation 30 ticks every second

		for event in pygame.event.get():
			# if click red X, quit game
			if event.type == pygame.QUIT:
				run = False

				pygame.quit()
				quit()
		

		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].get("x") > pipes[0].get("x") + pipes[0].PIPE_TOP.get_width():
				pipe_ind = 1

		else:
			run = False
			break

		for x, bird in enumerate(birds):
			ge[x].fitness += 0.1
			bird.move()

			# output from the neural network
			output = nets[x].activate((bird.get("y"), abs(bird.get("y") - pipes[pipe_ind].height), abs(bird.get("y") - pipes[pipe_ind].bottom)))

			# the output layer is a list, but we only have one neuron so only need to check once
			if output[0] > 0.5:
				bird.jump()

		# bird.move()
		base.move()

		# add and remove pipes
		rem = []
		add_pipe = False
		for pipe in pipes:
			pipe.move()
			# check for collision
			for x, bird in enumerate(birds):
				if pipe.collide(bird):
					ge[x].fitness -= 1	# deduct fitness score for birds who are hitting objects
					birds.pop(x)		# remove bird genomes who have hit objects
					nets.pop(x)
					ge.pop(x)

			
			if pipe.get("x") + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)

			if not pipe.get_passed() and pipe.get("x") < bird.get("x"):
				pipe.set_passed(True)
				add_pipe = True




		if add_pipe:
			score += 1
			
			for g in ge:
				g.fitness += 5	# reward the bird genomes that are still alive

			pipes.append(Pipe(600))

		for r in rem:
			pipes.remove(r)

		# check if bird has hit the ground
		for x, bird in enumerate(birds):
			if bird.get("y") + bird.img.get_height() >= 730 or bird.get("y") < -50:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)


		base.move()
		draw_window(win, birds, pipes, base, score, GEN)



def run(config_path):
	'''
	load the neat configuration file and execute
	'''
	import pickle

	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)


	# set the population
	p = neat.Population(config)

	# receive the output
	p.add_reporter(neat.StdOutReporter(True))	# gives stats
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)


	# fitness function
	winner = p.run(eval_genomes, 50)

	with open('bestBird.pickle', 'wb') as f:
		pickle.dump(winner, f, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
	local_directory = os.path.dirname(__file__)
	config_path = os.path.join(local_directory, "config-feedforward.txt")

	run(config_path)
