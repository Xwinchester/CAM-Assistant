
"""
globals
nci_file = nci text file
    list of a diction with the following values
        code = function call
        data = code
return modified nci code to update the text file
"""


def PROGRAM_START(*code):
    return "%"

def PROGRAM_NAME(*code):
    return " ".join(code)

def PROGRAM_END(*code):
    return "%"