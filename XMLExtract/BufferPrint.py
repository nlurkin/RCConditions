'''
Created on Aug 6, 2015

@author: nlurkin
'''

import sys
import os
import string
import tty, termios

def enum(*sequential, **named):
    """
    Create enums in python
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# termManip enums
color = enum(BLACK=30, RED=31, GREEN=32, YELLOW=33, BLUE=34, PURPLE=35, CYAN=36, WHITE=37)
modifier = enum(NORMAL=0, BOLD=1, UNDERLINE=4, BACKGROUND=10)

# Key Operation control enum
OperationType = enum("FORWARD_SCREEN", "FORWARD_LINE" ,"BACKWARD_LINE", "WRITE", "QUIT")

class PartialFormatter(string.Formatter):
    """
    Class that extends string format and correctly handles missing
    and wrong format fields.
    """
    def __init__(self, missing='~', bad_fmt='!'):
        self.missing, self.bad_fmt=missing, bad_fmt

    def get_field(self, field_name, args, kwargs):
        # Handle a key not found
        try:
            val=super(PartialFormatter, self).get_field(field_name, args, kwargs)
            # Python 3, 'super().get_field(field_name, args, kwargs)' works
        except (KeyError, AttributeError):
            val=None,field_name 
        return val 

    def format_field(self, value, spec):
        # handle an invalid format
        if value==None: return self.missing
        try:
            return super(PartialFormatter, self).format_field(value, spec)
        except ValueError:
            if self.bad_fmt is not None: return self.bad_fmt   
            else: raise

class termManip():
    """
    Class that contains terminal manipulation methods
    """
    
    @staticmethod
    def getColor(*col):
        """
        Returns the code string for a specific list of modifiers
        """
        codeList = []
        adder = 0
        for el in col:
            if el==modifier.BACKGROUND:
                adder = el
            else:
                codeList.append(str(el+adder))
                adder = 0
        return "\033[{0}m".format(";".join(codeList))
    
    @staticmethod
    def setColor(*col):
        print termManip.getColor(*col),
    
    @staticmethod
    def reset():
        print termManip.getReset(),
        
    @staticmethod
    def getReset():
        return "\033[0m"
    
    @staticmethod
    def setCursorTopLeft():
        print "\033[0;0f",

    @staticmethod
    def setCursorBottomLeft():
        termHeight = int(os.popen('stty size', 'r').read().split()[0])
        print "\033[{};0f".format(termHeight),
        
    @staticmethod
    def clearScreen():
        print "\033[2J",

def getch():
    """
    Wait and returns a character from stdin
    """
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def waitOperation():
    """
    Wait for keyboard operation
    space/enter: FORWARD_SCREEN
    down:        FORWARD_LINE
    up:          BACKWARD_LINE
    q:           QUIT
    w:           WRITE
    """
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
    elif ch==119:
        return OperationType.WRITE
    
def displayBuffer(stringBuffer):
    """
    Takes a long string buffer and displays slices of it on screen.
    Allows navigation through the slices with keyboard
    """
    length = 0
    newLength = 0
    doQuit = False
    termLen = int(os.popen('stty size', 'r').read().split()[0])-3
    stringBuffer = stringBuffer.split("\n")
    bufferLen = len(stringBuffer)
    while not doQuit:
        length = newLength
        termManip.clearScreen()
        termManip.setCursorTopLeft()
        for line in stringBuffer[length:length+termLen]:
            print line
        termManip.setCursorBottomLeft()
        print termManip.getColor(color.BLACK, modifier.BACKGROUND, color.WHITE)+\
            "Up/Down arrows to navigate   Space/Enter to skip 1 screen   w to write file   q to exit"+\
            termManip.getReset(),
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
                return opType
            elif opType==OperationType.WRITE:
                return opType

            if newLength<0:
                newLength=0
            elif (newLength+termLen)>bufferLen:
                newLength = bufferLen-termLen    

    
