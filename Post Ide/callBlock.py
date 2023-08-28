from enum import Enum

class CallBlock(Enum):
    """
    section to store the function to run and what the code is out of the nci
    """
    NULL_TOOL_CHANGE = {"code": "1000", "function": "NULL_TOOL_CHANGE"}
    START_OF_FILE_TOOL_CHANGE = {"code":"1001", "function":"START_OF_FILE_TOOL_CHANGE"}
    TOOL_CHANGE = {"code":"1002", "function":"TOOL_CHANGE"}
    END_OF_FILE     = {"code":"1003", "function":"END_OF_FILE"}
    CANCEL_CUTTER_COMP = {"code":"1004", "function":"CANCEL_CUTTER_COMP"}
    MANUEL_ENTRY_COMMENT = {"code": "1005", "function": "MANUEL_ENTRY_COMMENT"}
    MANUEL_ENTRY_CODE = {"code": "1006", "function": "MANUEL_ENTRY_CODE"}
    OPERATION_COMMENT = {"code": "1008", "function": "OPERATION_COMMENT"}
    MISCELLANEOUS_REALS = {"code": "1011", "function": "MISCELLANEOUS_REALS"}
    MISCELLANEOUS_INTEGERS = {"code": "1012", "function": "MISCELLANEOUS_INTEGERS"}
    MISCELLANEOUS_PARAMETERS = {"code": "1013", "function": "MISCELLANEOUS_PARAMETERS"}
    TOOL_PLANE_MATRIX = {"code": "1014", "function": "TOOL_PLANE_MATRIX"}








    DEFINE_VERSION_HEADER   = {"code":"1050", "function":"DEFINE_VERSION_HEADER"}
    MACHINE_GROUP_NAME    = {"code": "1053", "function": "MACHINE_GROUP_NAME"}
    NULL = {"code":"NULL", "function":"NULL"}