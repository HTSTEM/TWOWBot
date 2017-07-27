import re

def wrap_text(text,width,font,drawer):
    
    text_list = [text]
    
    while drawer.textsize(text_list[-1],font)[0] > width:
        nearest_space = get_nearest_space(text_list[-1],width,font,drawer)
        first = text_list[-1][:nearest_space]
        second = text_list[-1][nearest_space:]
        text_list[-1] = first
        text_list.append(second)
        
    return '\n'.join(text_list)
        
    
    
def get_nearest_space(text,width,font,drawer):

    text_width = drawer.textsize(text,font)[0]
    
    if width > text_width:
        return len(text)
    
    guess = len(text)*width // text_width
    
    while drawer.textsize(text[:guess],font)[0] < width:
        guess +=1
        
    while drawer.textsize(text[:guess],font)[0] > width:
        guess -= 1
        
    char_num = guess
    
    while char_num > 0:
        if text[char_num] == ' ':
            return char_num+1
        char_num -= 1
        
    return guess
    
def simplify(text):
    text = text.strip()
    text = re.sub('[^a-zA-Z0-9\(\)\[\]\{\}; ]','',text)
    
    return text