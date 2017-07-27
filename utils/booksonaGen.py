from PIL import Image, ImageChops
import sys

def makeLetterTint(char): 
	char = char.upper()
	hue1 = 0
	charCode = ord(char)

	if (char >= '0' and char <= '9'):
		hue1 = (charCode - ord('0')) / 10
	else:
		hue1 = (charCode - ord('A')) / 26 % 1
		
	sat1 = .7 - max(0, .15 - abs(hue1 - 2/3)) * 2

	hue360 = hue1 * 255
	sat100 = sat1 * 100
	return (int(hue360),153,255)
	
def make_book(name,dir):
	orig = name
	if len(name)<2:
		name += name
		
	left = Image.open('./resources/left.png').convert('RGBA')
	right = Image.open('./resources/right.png').convert('RGBA')
	face = Image.open('./resources/face.png').convert('RGBA')
	
	#left = ImageChops.multiply(left, Image.new('HSV', left.size, makeLetterTint(name[0])).convert('RGBA'))
	#right = ImageChops.multiply(right, Image.new('HSV', right.size, makeLetterTint(name[1])).convert('RGBA'))
	
	left.paste(right,(0,0),right)
	left.paste(face,(0,0),face)

	left.save('{}/{}.png'.format(dir,orig))
	

	
if __name__ =='__main__':
	try:
		file = sys.argv[1]
		names = open(file,'r').read().split('\n')
		for name in names:
			if not name == '':
				make_book(name,'./booksonas')
	except:
		while True:
			make_book(input(),'./booksonas')
			
	
	
		
