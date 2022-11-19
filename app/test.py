import time
test1 = 0

print(test1)
def loop():
    global test1
    test1 += 1
    time.sleep(1)
    print(test1)

while True:
    loop()