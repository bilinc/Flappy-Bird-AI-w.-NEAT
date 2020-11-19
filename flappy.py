import pygame
import neat
import time
import os
import random

# Constants for window size
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Load images for game
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

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


def draw_window(win, bird):
	# draw in the window at the top left position
	win.blit(BG_IMG, (0,0))
	bird.draw(win)
	pygame.display.update()

def main():
	bird = Bird(200, 200)
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	
	clock = pygame.time.Clock()

	run = True
	while run:
		clock.tick(30)	# animation 30 ticks every second
		for event in pygame.event.get():
			# if click red X, quit game
			if event.type == pygame.QUIT:
				run = False
		
		bird.move()
		draw_window(win, bird)

	pygame.quit()
	quit()

main()