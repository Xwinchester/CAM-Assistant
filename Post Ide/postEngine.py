
from callBlock import CallBlock

class PostEngine:

    def __init__(self):
        self.__raw_nci = []
        self.__current_code = []

    def __pre_process_raw_nci(self, nci):
        """
        takes in raw nci code as a string
        outputs the raw nci code into a list of a dictionary.
        code: is the type of data being used.
        data: is the actual data with the code
        """
        self.__raw_nci.clear()
        for i in range(0, len(nci), 2):
            if nci[i+1]:
                block = self.__process_code(nci[i])
                formatted_dict = {'code':nci[i], 'data':nci[i+1], 'block':block}
                self.__raw_nci.append(formatted_dict)

    def __process_code(self, code):
        """
        takes in the code from preprocess raw nci
        finds what the code is and uses the call block to determine what is being done
        returns the code and adds it to the dictionary
        """
        for member in CallBlock:
            # strips the code string
            code = code.strip()
            block_code = member.value.get("code")
            if code == block_code:
                return member
        else:
            return CallBlock.NULL
    def input_nci(self, content):
        nci = content.split("\n")
        self.__pre_process_raw_nci(nci)

    def get_raw_nci_string(self):
        return "\n".join([f"{nci['code']}\n{nci['data']}" for nci in self.__raw_nci])

    def get_raw_nci_list(self):
        return self.__raw_nci

    def post(self, script):
        formatted_code = []
        script_globals = {}
        # grab the script to format the code
        exec(script, script_globals)
        # loop through the raw nci list
        for nci in self.__raw_nci:
            # initialize the content
            content = None
            # grab the function from the CallBlock to run
            function = nci['block'].value.get("function")
            # grab the data from the nci list
            data = nci['data']
            # if function exists in the script, run it with the data from the nci data
            if function in script:
                content = script_globals[function](data)
            if content != None:
                formatted_code.append(content)
        return "\n".join(formatted_code)




