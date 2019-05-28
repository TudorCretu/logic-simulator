"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
from names import Names # remove this later 
import sys
class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    line_number -  this stores the line number of the symbol's location
    
    cursor_pos_at_start_of_line - this stores the cursor postition at the
                                  beginning of the line that contains the
                                  symbol

    Public methods
    --------------
    No public methods.
    """

    def __init__(self,line_number=None, cursor_pos_at_start_of_line=None):
        """Initialise symbol properties."""
        self.type = None
        
        #Note that id is the index in a name list for the types NAME and KEYWORD
        #For other types like NUMBER however, id is the actual value of the symbol 
        self.id = None 
        self.cursor_position = None
        self.line_number = line_number
        self.cursor_pos_at_start_of_line = cursor_pos_at_start_of_line
        


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
        #Set line number counter to 1
        #Set position of 1st character on current line to 1.
        self.names = names 
        self.symbol_type_list = [self.DOT, self.BACKSLASH, self.COMMA, self.SEMICOLON,
            self.EQUALS, self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(9)
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITORS"]
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITORS_ID] = self.names.lookup(self.keywords_list)
        self.current_character = self.file.read(1)
        self.line_number = 1
        self.cursor_pos_at_start_of_line = 0


    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        
        # skip past single and multi - line comments
        self.skip_comments() 
        symbol = Symbol(self.line_number, self.cursor_pos_at_start_of_line)
        # get cursor position at start of symbol
        symbol.cursor_position = self.file.tell() - 1
        # print(symbol.cursor_position,":test if cursor pos(left) None ")
        # Check for various symbol types
        if self.current_character.isalpha(): # name
            
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit(): # number
            symbol.id = self.get_number()
            symbol.type = self.NUMBER
            
        elif self.current_character == ".": # and so on ...
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
            # An invalid symbol type corresponds to a symbol
            # with default type and id of None and None
            
            self.advance()
            
        return symbol 
    
    def update_line_data(self):
        """Handle update of line number and cursor position at line beginning"""
        
        self.line_number +=1 
        self.cursor_pos_at_start_of_line = self.file.tell() 

    def advance(self):
        """Read ahead 1 character in the file"""
        if self.current_character == "\n":
            self.update_line_data()
            
        self.current_character = self.file.read(1)
        return self.current_character
          
    def skip_single_line_cmt(self):
        """Skip past single line comments"""
        self.file.readline() # progress to the end of line           
        self.advance() # progress to first character on new line
        self.update_line_data() 
        self.cursor_pos_at_start_of_line = self.cursor_pos_at_start_of_line - 1 
        # single line comments need to subtract 1 from cursror position due to
        # effects of /n 
    
    def skip_mult_line_cmt(self):
        """Skip to end of multiline comment or end of file"""
        self.advance() # move to first character after the '*'
        
        # keep skipping characters until the end of the M-L comment (*)
        # or the end of the file is reached
        while self.current_character !='*' and self.current_character !='':
            self.advance()
            
        self.advance() # move on to the next character
    
    def skip_comments(self):
        """Keeps skipping until we reach a non - comment - initiating
        character """
        self.skip_spaces() # move to next non - whitespace character 
        
        # The specific comment punctuation is landed on determines
        # the type of comment that will have to be skipped past
                
        if self.current_character == '#': # '#' marks single line comments
            self.skip_single_line_cmt()
        
        elif self.current_character == '*': # '*' initiates a multi - line comment
            self.skip_mult_line_cmt()
        
        else:
            return # indicates we did not land on a comment starting 
                   # character, ending the process
        
        self.skip_comments() # keep repeating until we don't land on a 
                             # comment starting character
    
    
    def skip_spaces(self):
        """Skip to the next non - white space character in the file"""
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
    
    def show_error_location(self,line_number, cursor_pos_at_start_of_line,
                               last_symbol_cursor_pos):
        """Returns information about the location of an error. Shows the file 
        that contains it, the line number of the error and the specific
        point on that line where the error occurs"""
                
        pos_of_err = last_symbol_cursor_pos
        # find the collumn number of the error location within the line
        caret_coll_num = pos_of_err - cursor_pos_at_start_of_line
 
        # move cursor to start of current line
        self.file.seek(cursor_pos_at_start_of_line)

        # add a caret to the point where the error begins on current line 
        # display all error location information referred to above        
        line = self.file.readline()
        
       
        Line_rdt ='Line ' + str(line_number) + ': ' + line[:-1] + '\n'
        
        output = Line_rdt + (caret_coll_num +len(str(line_number))+7) *' '+ '^' + ' '*(len(line)-1-caret_coll_num)
        print(output)


        #output1 = 'File : ' + self.file.name + '\n'      
        
        #output = 'Line ' + str(line_number) + ' : ' + line_with_caret

        #print (output) # must be removed later
        return output #+ output2

#
#
names = Names()
scanner = Scanner('test_functions/read_symbol.txt',names)
symbol = None
for a in range(3):
    symbol =scanner.get_symbol()
    '''
    try:
        print(symbol.type,names.get_name_string(symbol.id))
    except:
        print(symbol.type,symbol.id)
    scanner.display_error_location(symbol.cursor_position)
    '''
    print (symbol.cursor_position,symbol.cursor_pos_at_start_of_line,symbol.line_number)
    scanner.show_error_location(symbol.line_number,symbol.cursor_pos_at_start_of_line,symbol.cursor_position)
    
#scanner.display_error_location(symbol.cursor_position)

#scanner.display_error_location(1,0,0)
#scanner.display_error_location(7,7,5)
#canner.display_error_location(7,10,10)
