from enum import Enum

class CallBlock(Enum):
    """
    section to store the function to run and what the code is out of the nci
    """
    PROGRAM_START   = {"code":"1050", "function":"PROGRAM_START"}
    PROGRAM_NAME    = {"code": "1053", "function": "PROGRAM_NAME"}
    PROGRAM_END     = {"code":"1003", "function":"PROGRAM_END"}
    NULL = {"code":"NULL", "function":"NULL"}