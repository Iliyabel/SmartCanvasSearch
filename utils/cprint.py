class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    print(f"{bcolors.HEADER}{text}{bcolors.ENDC}")

def print_status(text):
    print(f"{bcolors.OKGREEN}{text}{bcolors.ENDC}")

def print_warning(text):
    print(f"{bcolors.WARNING}{text}{bcolors.ENDC}")
