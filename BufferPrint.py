'''
Created on Aug 6, 2015

@author: nlurkin
'''

from XMLExtract import TEL62Decoder
import sys
import os

color = "\033[33;1m"

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

OperationType = enum("FORWARD_SCREEN", "FORWARD_LINE" ,"BACKWARD_LINE", "QUIT")

def getch():
    import tty, termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def waitOperation():
    ch = ord(getch())
    if ch==13 or ch==32:
        return OperationType.FORWARD_SCREEN
    elif ch==27:
        if ord(getch())==91:
            #arrow key
            ch = ord(getch())
            if ch==65:
                return OperationType.BACKWARD_LINE
            elif ch==66:
                return OperationType.FORWARD_LINE
    elif ch==113:
        return OperationType.QUIT
    
def displayBuffer(stringBuffer):
    length = 0
    newLength = 0
    doQuit = False
    termLen = int(os.popen('stty size', 'r').read().split()[0])-3
    stringBuffer = stringBuffer.split("\n")
    bufferLen = len(stringBuffer)
    while not doQuit:
        length = newLength
        for line in stringBuffer[length:length+termLen]:
            print line
        print ""
        print "Up/Down arrows to navigate   Space/Enter to skip 1 screen   q to exit"
        while newLength==length and not doQuit:
            opType = waitOperation()
            if opType==OperationType.FORWARD_SCREEN:
                newLength += termLen
            elif opType==OperationType.FORWARD_LINE:
                newLength += 1
            elif opType==OperationType.BACKWARD_LINE:
                newLength -= 1
            elif opType==OperationType.QUIT:
                doQuit = True

            if newLength<0:
                newLength=0
            elif (newLength+termLen)>bufferLen:
                newLength = bufferLen-termLen    

if __name__ == "__main__":
    xmldoc = TEL62Decoder(sys.argv[1])
    displayBuffer(str(xmldoc))
    
