import time
now = 0

while True:
    if time.time() - now > 10:
        print "time up"
        now = time.time()

