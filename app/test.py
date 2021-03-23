from queue import Queue
from queue import Empty

p = Queue()
p.put('1')
p.put('2')
p.put('3')
p.put('4')

while True:
    try:
        e = p.get(block=False)
        print(e)
    except Empty:
        break

print('fine')