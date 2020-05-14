from PIL import Image,ImageDraw,ImageFont
import epd2in7b
import epdconfig

font20 = ImageFont.truetype('fonts/arial.ttf', 20)

def display_coffee(epd):
    '''
    Given an EPD instance, render a coffee image on the screen.
    '''

    blackimage1 = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    redimage1 = Image.new('1', (epd.width, epd.height), 255)  # 298*126    

    drawred = ImageDraw.Draw(redimage1)
    drawred.text((20, 240), 'Coffee break :-)', font = font20, fill = 0)

    coffe_image = Image.open('img/coffee2.bmp')
    blackimage1.paste(coffe_image, (15,5))    

    epd.display(epd.getbuffer(blackimage1), epd.getbuffer(redimage1))
