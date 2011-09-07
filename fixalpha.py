#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
try:
	from PIL import Image 
except ImportError:
	import Image
from ui import ProgressBar

def remove_alpha(im):	
	(w,h) = im.size
	data = im.load()
	for x in xrange(w):
		for y in xrange(h):
			(r, g, b, a) = data[x, y]
			data[x, y] = (r, g, b, 255)
	return im


class ImageTable(object):
	def __init__(self, im):
		(w, h) = im.size
		self.colors = im.load()
		self.width = w
		self.height = h
		self.data = [ 0 for x in xrange(w * h) ]
		
		
	def get(self, p):
		(x, y) = p
		return self.data[y * self.width + x]
		
	def put(self, p, value):
		(x, y) = p
		self.data[y * self.width + x] = value
		
	def is_inside(self, p):
		(x, y) = p
		if x < 0: return False
		if y < 0: return False
		if x >= self.width: return False
		if y >= self.height: return False
		return True
		
	def neighbour_positions(self, p, radius=1):
		(x, y) = p
		w = self.width
		h = self.height
		for m in xrange(x-radius, x+radius+1):
			if m < 0: continue
			if m >= w: continue
			for n in xrange(y-radius, y+radius+1):
				if n < 0: continue
				if n >= h: continue
				if m == x and n == y: continue
				yield (m, n)
				
	def positions(self):
		for y in xrange(self.height):
			for x in xrange(self.width):
				yield (x, y)
				
	def color(self, p):
		(x, y) = p
		return self.colors[x, y]
		
	def set_color(self, p, color):
		(x, y) = p
		self.colors[x, y] = color
		
	def mark(self, value, old=0, surrounds=1):
		w = self.width 
		h = self.height
		result = []
		
		# extend edge with 2
		i = -1
		for y in xrange(h):
			for x in xrange(w):
				i += 1
				v = self.data[i]
				if v != old: continue
	
				found = False
				for (m, n) in self.neighbour_positions((x,y)):
					if self.data[n * w + m] == surrounds:
						found = True
						break
						
				if found:
					self.data[i] = value
					result.append((x,y))
		return result


class Progress(object):
	def __init__(self, title, max_value):
		self.counter = 0
		self.title = title
		self.progress = ProgressBar(0, max_value/100, mode='fixed')
	
	def increase(self):
		self.counter += 1
		if self.counter % 100 == 0:
			self.progress.increment_amount()
			print '%-20s' % self.title, '\t', self.progress, '\r',
			sys.stdout.flush()
			
def solidify(im, ratio=128, title=None):
	table = ImageTable(im)
	
	counter = 0
	progress = Progress(title, max_value=len(table.data))
		
	
	# mark mask 
	for p in table.positions():
		(r,g,b,a) = table.color(p)
		if a > ratio:
			table.put(p, 1)
			progress.increase()
		else:
			table.put(p, 0)
	
	queue = table.mark(2, old=0, surrounds=1)
	
	while queue:
		p = queue.pop(0)
		v = table.get(p)
		(r,g,b,a) = table.color(p)
		
		colors = []
		for n in table.neighbour_positions(p, radius=1):
			nv = table.get(n)
			# looking for previous generation
			if nv == 0:
				table.put(n, v+1)
				queue.append(n)
			elif nv > v+1:
				table.put(n, v+1)
				if n not in queue:
					queue.append(n)
			elif nv < v:
				colors.append(table.color(n))
				
		if not colors:
			print p, v
			for n in table.neighbour_positions(p):
				nv = table.get(n)
				print 'neighbour', n, nv
			raise Exception("What the heck!?")
		
		# average colors
		sr = 0.0
		sg = 0.0
		sb = 0.0
		total = 0
		for (nr,ng,nb,na) in colors:
			sr += nr
			sg += ng
			sb += nb
			total += 1		
			
		table.set_color(p, (int(sr/total), int(sg/total), int(sb/total), a))
		progress.increase()

	progress.increase()
	print ""
			
	return im
		
		
def main():
	files = os.listdir('input')
	files.sort()
	for filename in files:
		inputfile = os.path.join('input', filename)
		outputfile = os.path.join('output', filename)
		im = Image.open(inputfile).convert('RGBA')
		im = solidify(im, ratio=10, title=filename)
		# im = remove_alpha(im)
		im.save(outputfile)
	
if __name__ == '__main__':
	sys.exit(main())


