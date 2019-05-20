"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

import sys

class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        
        #Note that id is the index in a name list for the types NAME and KEYWORD
        #For other types like NUMBER however, id is the actual value of the symbol 
        self.id = None 


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        try : # open file using path
            self.file = open(path)
        except FileNotFoundError:
            print("File was not found.")
            sys.exit()
        
        #Initialise instance of Names class , list of symbol types,
        #list of keywords as well as ID values for keywords
        #Set current_character attribute to first character of file
        self.names = names 
        self.symbol_type_list = [self.DOT, self.BACKSLASH, self.COMMA, self.SEMICOLON,
            self.EQUALS, self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(9)
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITORS"]
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITOR_ID] = self.names.lookup(self.keywords_list)
        self.current_character = self.file.read(1)



    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()
        while self.current_character == "#":
            self.skip_comment()
            self.skip_spaces() # current character now not whitespace
        
        
        if self.current_character.isalpha(): # name
            
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit():
            symbol.id = self.get_number()
            symbol.type = self.NUMBER
            
        elif self.current_character == ".":
            symbol.type = self.DOT
            self.advance()

        elif self.current_character == "=":
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == "/":
            symbol.type = self.BACKSLASH
            self.advance()

        elif self.current_character == ",":
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == "":          
            symbol.type = self.EOF

        else:
            self.advance()
            

        return symbol 

    def advance(self):
        """Read ahead 1 character in the file"""
        self.current_character = self.file.read(1)
        return self.current_character

    def skip_comment(self):
        """Once a # is reached, skip to next line"""
        if self.current_character == '#':
            self.file.readline()
            self.advance()
        
        
        
    def skip_spaces(self):
        """Skip to the non - white space character in the file"""
        while self.current_character.isspace():
            self.advance()

    def get_name(self):
        """Obtain the next name symbol in the file"""
        name = ''
        while self.current_character.isalnum() :
            name += self.current_character
            self.advance()
        return name 
        

    def get_number(self):
        """Obtain the next number symbol in the file"""
        number = ''
        while self.current_character.isdigit() :
            number += self.current_character
            self.advance()
        return number 