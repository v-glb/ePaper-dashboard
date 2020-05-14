### Imports
import sys
sys.path.append(r'lib')
from datetime import datetime, timedelta, time
import caldav
import signal
import epd2in7b
import epdconfig
import time
from PIL import Image,ImageDraw,ImageFont
from config import nextcloud_url

### Nextcloud calendar URL from config
url = nextcloud_url

### Fonts for epd rendering
font24 = ImageFont.truetype('fonts/arial.ttf', 24)
font16 = ImageFont.truetype('fonts/arial.ttf', 16)
font20 = ImageFont.truetype('fonts/arial.ttf', 20)

def show_todos(epd):
  '''
  Given an EPD instance, fetch todos from Nextcloud tasks and render them on the display.
  '''

  client = caldav.DAVClient(url)
  principal = client.principal()
  # Get all calendars associated with user v
  calendars = principal.calendars()
  # Get single personal calendar for todos
  calendar = caldav.Calendar(client=client, url=url)

  if len(calendars) > 0:

    # Sort todos based on creation date
    todos = calendar.todos(sort_keys=('created',))

    # Prepare display for rendering
    LBlackimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
    LRedimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
    drawblack = ImageDraw.Draw(LBlackimage)
    drawred = ImageDraw.Draw(LRedimage)

    newimage = Image.open('img/todo.bmp')
    LBlackimage.paste(newimage, (12,0)) 

    # Gather todos from calendar personal
    if len(todos) == 0:
      drawblack.text((2, 60), "Nothing to do! :)", font = font24, fill = 0)

    else:
      position_counter = 40 

      for todo in todos:
        todo.load()
        t = todo.instance.vtodo
        todoCreated = t.created.value.strftime("%Y-%m-%d %H:%M:%S")

        drawblack.text((2, position_counter), "- " + t.summary.value, font = font16, fill = 0)
        position_counter += 20


    epd.display(epd.getbuffer(LBlackimage), epd.getbuffer(LRedimage))

  else:
    print("Calendar with todos not found!")

