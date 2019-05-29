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
        self.cursor_position = None
        self.line_number = line_number
        self.cursor_pos_at_start_of_line = cursor_pos_at_start_of_line
        self.id = None

        # Note that id is the index in a name list for the types NAME and
        # KEYWORD. For other types like NUMBER however, id is the actual value
        # of the symbol



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

        # Initialise instance of Names class , list of symbol types,
        # list of keywords as well as ID values for keywords
        # Set current_character attribute to first character of file
        # Set line number counter to 1
        # Set position of 1st character on current line to 0.
        self.names = names
        self.symbol_type_list = [self.DOT, self.FORWARDS_SLASH, self.COMMA
                                 ,self.SEMICOLON, self.EQUALS, self.KEYWORD
                                 , self.NUMBER, self.NAME, self.EOF] = range(9)
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITORS"]
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITORS_ID] = (
                self.names.lookup(self.keywords_list))
        self.current_character = self.file.read(1)
        self.line_number = 1
        self.cursor_pos_at_start_of_line = 0


    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""

        # skip past single and multiline comments before initialising a new
        # symbol object with relevant attributes
        # NOTE : we subtract 1 for the cursor_position attribute since
        # the skip self.comments() leads to the first character of the
        # symbol being read in ( i.e the cursor 'moves past' it)
        self.skip_comments()
        symbol = Symbol(self.line_number, self.cursor_pos_at_start_of_line)
        symbol.cursor_position = self.file.tell() - 1

        # Obtain the type of the symbol based on the first character read in
        if self.current_character.isalpha(): # NAME type case

            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit(): # NUMBER type case
            symbol.id = self.get_number()
            symbol.type = self.NUMBER

        elif self.current_character == ".": # and so on ...
            symbol.type = self.DOT
            self.advance()

        elif self.current_character == "=":
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == "/":
            symbol.type = self.FORWARDS_SLASH
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
        """Handle update of line number and cursor position at line start"""
        self.line_number +=1
        self.cursor_pos_at_start_of_line = self.file.tell()

    def advance(self):
        """Read ahead 1 character in the file and return it"""

        # if a new line transition is reached update line and cursor position
        # information
        if self.current_character == "\n":
            self.update_line_data()

        self.current_character = self.file.read(1)
        return self.current_character

    def skip_single_line_cmt(self):
        """Skip past single line comments"""
        self.file.readline()  # progress to the end of line
        self.update_line_data()
        self.advance()  # progress to first character on new line


    def skip_mult_line_cmt(self):
        """Skip to end of multiline comment or end of file"""
        self.advance() # move to first character after the '*'

        # keep skipping characters until the end of the M-L comment (*)
        # or the end of the file is reached
        while self.current_character !='*':
            
            # if unclosed M-L comment present , provide warning
            if (self.current_character == ''):
                print("** WARNING : UNCLOSED MULTILINE COMMENT PRESENT: "
                      "IT IS RECOMMENDED THAT YOU CLOSE IT WITH A '*'")
                return

            self.advance()

        self.advance()  # move on to the next character after the M-L comment

    def skip_comments(self):
        """Keeps skipping until we reach a non - comment - initiating
        character """
        self.skip_spaces() # move to next non - whitespace character

        # The specific comment punctuation is landed on determines
        # the type of comment that will have to be skipped past
        
        # '#' marks single line comments
        if self.current_character == '#':
            self.skip_single_line_cmt()
        
        # '*' initiates a multiline comment
        elif self.current_character == '*':
            self.skip_mult_line_cmt()
            
        # Otherwise we did not land on a comment-starting character so end
        else:
            return

        # keep repeating until we don't land on a comment -starting char
        self.skip_comments()

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
                            cursor_pos_of_err):
        """Returns information about the location of an error. Shows the file
        that contains it, the line number of the error and the specific
        point on that line where the error occurs.

        The parser will call this function specifying the line number of the
        error, the cursor position at the start of said line and finally the
        cursor position of the error (typically the first character of the
        error symbol)"""

        # find the collumn number of the error location within the line
        caret_coll_num = cursor_pos_of_err - cursor_pos_at_start_of_line

        # move cursor to start of current line
        self.file.seek(cursor_pos_at_start_of_line)

        # obtain the full line of the error
        line = self.file.readline()
        
        # remove any trailing '\n' characters from the line
        if (len(line) != 0):
            if (line[len(line)-1]=='\n'):
                line = line[:-1]

        # obtain the first line of the error location information output
        out1 = 'Line ' + str(line_number) + ': ' + line + '\n'

        # obtain the second line of the output (here the caret is placed
        # at after an appropriately sized displacement string of spaces
        leading_spaces = caret_coll_num+len(str(line_number))+7
        trailing_spaces = len(line)-1-caret_coll_num
        out2 = leading_spaces*' ' + '^' + trailing_spaces*' '

        # return the overall error location information
        output = out1 + out2
        print(output)
        return output

#
#
'''
names = Names()
scanner = Scanner('test_functions/read_symbol.txt',names)
symbol = None
for a in range(3):
    symbol =scanner.get_symbol()

    try:
        print(symbol.type,names.get_name_string(symbol.id))
    except:
        print(symbol.type,symbol.id)
    scanner.display_error_location(symbol.cursor_position)

    print (symbol.cursor_position,symbol.cursor_pos_at_start_of_line,symbol.line_number)
    scanner.show_error_location(symbol.line_number,symbol.cursor_pos_at_start_of_line,symbol.cursor_position)

#scanner.display_error_location(symbol.cursor_position)

#scanner.display_error_location(1,0,0)
#scanner.display_error_location(7,7,5)
#canner.display_error_location(7,10,10)
'''