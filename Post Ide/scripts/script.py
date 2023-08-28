
"""
globals
nci_file = nci text file
    list of a diction with the following values
        code = function call
        data = code
return modified nci code to update the text file
"""


def START_OF_FILE_TOOL_CHANGE(*code):
    return "%"
def OPERATION_COMMENT(*code):
    return f"({code[0]})"
def PROGRAM_NAME(*code):
    return " ".join(code)

def TOOL_PLANE_MATRIX(*code):
    codea = "".join(code)
    codea.replace(" ", "")
    return None

def END_OF_FILE(*code):
    return "%"