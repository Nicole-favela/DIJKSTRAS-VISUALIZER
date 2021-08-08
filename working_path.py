
import pygame
from queue import PriorityQueue
from pygame import mixer

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Dijkstra's Algorithm Path Finder")

GREEN = (0, 204, 0)
DARKGREEN = (0, 102,0)
ROYALBLUE = (0,0,255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
GREY = (128, 128, 128) #grid color

class Square:
	def __init__(self, row, col, width, totalRows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = BLACK #background color
		self.neighbors = []
		self.width = width
		self.totalRows = totalRows

	def get_pos(self):
		return self.row, self.col

	def isClosed(self):
		return self.color == DARKGREEN

	def isOpen(self):
		return self.color == GREEN

	def isBarrier(self): #user drawn barrier path cannot cross
		return self.color == ROYALBLUE

	def isStart(self): #start square
		return self.color == PURPLE

	def isEnd(self): #end square
		return self.color == DARKGREEN

	def makeStart(self): #starting point set to purple
		self.color = PURPLE

	def makeClosed(self): #expanding path
		self.color = DARKGREEN

	def makeOpen(self): #outermost path
		self.color = GREEN

	def makeBarrier(self):
		self.color = ROYALBLUE

	def makeEnd(self): #user defined end square
		self.color = DARKGREEN

	def makePath(self):
		self.color = YELLOW

	def draw(self, win): #creates rectangles for game
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = [] #for list of neighbor squares
		#checks rows and columns that are not part of the barrier
		if self.row < self.totalRows - 1 and not grid[self.row + 1][self.col].isBarrier(): # vertical neighbor (down)
			self.neighbors.append(grid[self.row + 1][self.col]) #adds to list of valid neighbors 

		if self.row > 0 and not grid[self.row - 1][self.col].isBarrier(): #vertical neighbor (up)
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.totalRows - 1 and not grid[self.row][self.col + 1].isBarrier(): #horizontal neighbor (right)
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].isBarrier(): # horizontal neighbor (left)
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other): # for behavior of less than 
		return False


def pathDiscoveredSound():
	#TO DO
	#plays sound when path found
	pass
#plays music
def gameSound():
	#initialize mixer
	pygame.mixer.init()
	#background music for while visualization is in progress
	mixer.music.load('acdc_background.mp3')
	mixer.music.play(-1) #keep playing indefinitely 
#creates yellow shortest path at the end
def reconstructPath(visited, cur, draw):
	while cur in visited: 
		cur = visited[cur]
		cur.makePath() #makes shortest path
		draw()
#implements dijkstra's algorithm
def dijkstras(draw, grid, start, end):
	
	openQ= PriorityQueue() #stores distances that haven't been finalized, gets smallest item from queue
	openQ.put((0, start)) #starting node square is at distance 0, and start
	cameFrom = {} # dictionary that Stores path
	
	g_score = {}
	for row in grid:
		for square in row:
			g_score[square] = float("inf") #sets every edge to infininity
	g_score[start] = 0 #start is distance 0
	syncSet = {start} #used for checking if value is in openQ or not by using set

	while not openQ.empty(): #if openQ is empty we have considered all possible paths, so exit loop
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT:#quit if x clicked
				pygame.quit()

		cur = openQ.get()[1] #pops our current smallest node. at first cur = start node
		syncSet.remove(cur) #adds node we just popped into hash for validating purposes 

		if cur == end: #this means the path was found
			reconstructPath(cameFrom, end, draw) #draw path in yellow
			end.makeEnd() #fill in color
			return True

		for neighbor in cur.neighbors:
			temp_g_score = g_score[cur] + 1 #next node + 1 since it is one node over

			if temp_g_score < g_score[neighbor]: #better path
				cameFrom[neighbor] = cur #
				g_score[neighbor] = temp_g_score #what we need for djikstras: computes cost from start 
				if neighbor not in syncSet:
					openQ.put((g_score[neighbor], neighbor)) #better path
					syncSet.add(neighbor)
					neighbor.makeOpen() 
		draw()

		if cur != start:
			cur.makeClosed() #already considered

	return False #no path exists 


def makeGrid(rows, width):
	grid = []
	gap = width // rows
	for row in range(rows):
		grid.append([])
		for col in range(rows):
			sq = Square(row, col, gap, rows)
			grid[row].append(sq)
    
	return grid

#creates grey lines 
def drawGrid(win, rows, width):
	gap = width // rows
	for row in range(rows):
		pygame.draw.line(win, GREY, (0, row * gap), (width, row * gap))
		for col in range(rows):
			pygame.draw.line(win, GREY, (col * gap, 0), (col * gap, width))

#draws and updates display
def draw(win, grid, rows, width):
	win.fill(BLACK)
	for row in grid:
		for square in row:
			square.draw(win)

	drawGrid(win, rows, width)
	pygame.display.update()

#returns coordinates clicked
def clickedPos(pos, rows, width):
	gap = width // rows
	y, x = pos
	row = y // gap
	col = x // gap
	return row, col

def main(win, width):
	ROWS = 50
	grid = makeGrid(ROWS, width) #draws grid for squares
	start = None
	end = None

	running = True
	while running:
		
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if pygame.mouse.get_pressed()[0]: # Left mouse pressed
				
				pos = pygame.mouse.get_pos() 
				row, col = clickedPos(pos, ROWS, width) #gets location
				square = grid[row][col] #indexes grid 
				if not start and square != end:
					start = square
					start.makeStart()

				elif not end and square != start: 
					end = square
					end.makeEnd()

				elif square != end and square != start: 
					square.makeBarrier() #draws user defined barrier that cannot be crossed

			if event.type == pygame.KEYDOWN: #starts algorithm when space pressed and start and end defined 
				if event.key == pygame.K_SPACE and start and end:
					gameSound() #plays music 
					for row in grid:
						for square in row:
							square.update_neighbors(grid)

					dijkstras(lambda: draw(win, grid, ROWS, width), grid, start, end)

				if event.key == pygame.K_c: #undo start and end by pressing cmd + c 
					start = None
					end = None
					grid = makeGrid(ROWS, width)

	pygame.quit()

main(WIN, WIDTH)