import time, re, glob
import urllib.request

###############################################
###############################################
###                                         ###
###   A game of memorizing spider genera.   ###
###   (Ignore the very messy variables...)  ###
###                                         ###
###############################################
###############################################


###############################################
#              Various constants              #
###############################################

WIDTH = 100
INTERVAL = 10
TITLE = "SPIDER GENUS NAMING CHALLENGE"
SUMMARY = "\nThis is a simple game where you name as many genera from a spider family as you can.\
\nOnce you select a family, you will be prompted to submit genus names one at a time.\
\nThe taxon names don't need to be case-sensitive.\
\nIf you go 10 seconds without entering another valid genus name, the game ends!"


###############################################
#              Various functions              #
###############################################

# Print a divider of asterisks (default behavior: treat as new heading)
def print_divider(length,heading=True):
    if heading == True: print()
    divider = ""
    for i in range(0,length):
        divider = divider + "*"
    print(divider)

# Print line to be displayed within a box
def print_sides(length,content):
    text = content.center(length-2)
    print("*" + text.center(length-4) + "*")
    
# Print a header
def print_header(length,content):
    print_divider(length)
    print_sides(length,"")
    print_sides(length,content)
    print_sides(length,"")
    print_divider(length,False)

# Read a webpage as text
def get_webtext(url):
    with urllib.request.urlopen(url) as webpage:
        html = webpage.read()
        encoding = webpage.headers.get_content_charset('utf-8')
        decoded_html = html.decode(encoding)

    return decoded_html

# Prompt user for spider family and create answer key from World Spider Catalog
def get_genera():
    while True:
        print_divider(WIDTH)
        global user_family
        user_family = input("\nEnter the scientific name of the spider family you now wish to attempt: ").capitalize()

        print("Fetching genera from World Spider Catalog... ",end="")

        web_families = get_webtext("https://wsc.nmbe.ch/families")
        family_pattern = "(/[0-9]+/" + user_family + ")\">Genera<"
        family = re.compile(family_pattern)
        family_search = re.findall(family,web_families)

        if len(family_search) < 1:
            print("\n\n*** ERROR! Family name not found:", user_family, "***")
            continue
        else: break

    family_url = "https://wsc.nmbe.ch/genlist" + family_search[0]
    web_genera = get_webtext(family_url)
    genus = re.compile("[0-9]+/([A-z]+)\">Catalog<")
    genera_search = re.findall(genus,web_genera)
    global grandtotal
    grandtotal = len(genera_search)

    print(grandtotal, "found.\n\n")

    return genera_search

# Fetch previous personal record, if available, and create file otherwise
def get_pb(filename):
    try:
        with open(filename,"r") as pb_infile:
            pb = int(pb_infile.readlines()[-1])
    except:
        pb = 0
        with open(filename,"w") as pb_outfile:
            pass

    return pb

''' ### Commenting out this section for online experiment ###
# Display all current personal high scores
def get_scores():
    filelist = glob.glob("pb_for_*ae.txt")
    total_pb = 0
    if len(filelist) > 0:
        print_divider(WIDTH)
        print("\nCurrent personal records:")
        for filename in filelist:
            family_name = filename[7:-4]
            family_pb = get_pb(filename)
            total_pb = total_pb + family_pb
            print(family_name, "-", family_pb)
        print(total_pb, "genera total")
'''

# Calculate time remaining
def countdown(reference_time):
    curr_time = time.time()
    countdown_number = 10 - (curr_time - reference_time)

    return str(int(round(countdown_number,0)))

# Prompt for genus names
def prompt_genera(start, genera, pb, pb_filename):
    time_limit = str(INTERVAL)
    
    while True:
        #check the timer and act if the limit has been exceeded
        diff = time.time() - start
        if diff > INTERVAL:
            total = len(spiders)
            taxon_word = "genera"
            if total == 1: taxon_word = "genus"
            percentage = float(total) / float(grandtotal) * 100
            print("\n*** GAME OVER! Time's up. ", end="")
            if total > 0:
                print(str(round(diff,2)), "seconds elapsed since last valid entry. ",end="")
            print("***\n\nYou named a total of", total, taxon_word, "in", str(round(time.time()-first_start,2)), "seconds, or", round(percentage,2), end="")
            print("% of known genera for", user_family, end="")
            print(".\nYour previous record for this family was", str(pb) + ".", end="")
            if total > pb:
                print(".. congratulations on setting a new personal best!")
                with open(pb_filename,"a") as pb_outfile:
                    pb_outfile.write(str(total) + "\n")
            break
        
        #prompt another entry otherwise
        prompt_message = "Enter a genus within " + time_limit + " seconds: "
        next_spider = input(prompt_message).capitalize()
        
        #check that the entered genus name is valid and not a duplicate
        if next_spider not in genera:
            print("*** Not a genus in", user_family, "- check your spelling? ***\n")
            time_limit = countdown(start)
            continue
        elif next_spider in spiders:
            print("*** Already listed - entry number", spiders.index(next_spider)+1, "***\n")
            time_limit = countdown(start)
            continue
        spiders.append(next_spider)
        
        #refresh time values
        start = time.time()
        time_limit = str(INTERVAL)

# Gameplay pipeline
def play_game():
    genus_list = get_genera()
    
    pb_filename = "pb_for_" + user_family + ".txt"
    prev_pb = get_pb(pb_filename)

    global first_start, spiders
    start_time = time.time()
    first_start = start_time
    spiders = []

    prompt_genera(start_time, genus_list, prev_pb, pb_filename)

# Prompt user to quit or replay
def quit_or_replay():
    while True:
        user_response = input("\n\nWould you like to QUIT or REPLAY?\n>").lower()
        if user_response in ["quit", "q", "exit"]:
            print("*** Thanks for playing! ***\n")
            exit()
        elif user_response in ["restart", "replay", "retry", "r"]:
            play_game()
            break
        else:
            print("*** ERROR! I didn't understand that response. ***")
            continue
        

###############################################
#   Active gameplay begins after this point   #
###############################################

''' ### Commenting this out for online experiment ###
# Introduce the game
print_header(WIDTH,TITLE)
print(SUMMARY)

# get_scores()
'''

# Initiate gameplay loop
play_game()
while True: quit_or_replay()
