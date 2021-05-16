from pynput import keyboard as kb

def press(key):
    print('You have touch the key ' + str(key))

with kb.Listener(press) as listener:
    listener.join()