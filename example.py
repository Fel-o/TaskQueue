from datetime import datetime, timedelta
from TaskQueue import Task
from Bot import Bot

# create tasks
now = datetime.now()
a = Task(print, scheduled_time=now + timedelta(seconds=20), args=['a'], id='a')
b = Task(print, scheduled_time=now + timedelta(seconds=30), args=['b'], id='b')
c = Task(print, scheduled_time=now + timedelta(seconds=40), args=['c'], id='c')

# create and start Bot
bot = Bot('Bot1')
bot.start()

# scheduling can be done in a different thread
bot.schedule([a, b, c])
