
debug_level = 0

def debug_set_level(n):
    global debug_level
    debug_level = n

def debug_print(*argv):
    level = argv[0]
    if debug_level >= level:
        print("DEBUG:", end=" ")
        for i in argv[1:]:
            if type(i) == str:
                print(i.replace("\\n","\n"), end=" ")
            else:
                print(i, end=" ")
        print("")

