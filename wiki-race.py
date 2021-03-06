import wikiparser, sys, time
from os import get_terminal_size

'''
Hello! This is the file you care about if you want to race my wiki bot! For those in Visual Studio Code, press Alt + Z to make this wall of text easier to read.

I do want to note that the current implementation isn't horribly fast, as it has to iterate through every link from the given article in sequence. 
I spent several hours trying to create a faster version using Python's multiprocessing package, but there's a limit on how many times I can query Wikipedia at once and I haven't found anything that consistently avoids this issue. In my opinion, this is my number one priority.

I also want to point out that the solution generated by this bot isn't necessarily optimal. There are certainly cases where this is true, but I'm currently loading candidate articles into a PriorityQueue based on how many links they share with the destination article. As I see it, it makes much more sense to go for speed and make this something that a human can race against.

I'd like to cite some sources as well.

- For multiprocessing information, as well as knowledge about the time package.
    https://www.analyticsvidhya.com/blog/2021/04/a-beginners-guide-to-multi-processing-in-python/

- For general questions, StackOverflow and GeeksForGeeks. I was very careful to only take inspiration from StackOverflow and even then I didn't take much. I'm planning on using the following post if/when I go back through to add multiprocessing
    https://stackoverflow.com/questions/4827432/how-to-let-pool-map-take-a-lambda-function
- I did consult the following G4G article on os.get_terminal_size(), but I'm not sure there were other options there. 
    https://www.geeksforgeeks.org/python-os-get_terminal_size-method/

  

For Professor Wong / TAs for NEU's CS4100 course:

I'd like to get a handful of human benchmarks to compare the bot to, but I'm not in a position to do this before the initial draft is due. I'll be home for Christmas on the 11th and am hoping to get some tests during the following week.
'''

# user_input[0] is always "wiki-race.py"
# If user_input[1] or [2] exist, they're the initial and target articles, respectively
user_input = sys.argv

# if arguments are supplied
if len(user_input) == 3:
    initial = user_input[1]
    dest = user_input[2]
else:
    # Prompt user for initial article
    print("What is the initial article?")
    initial = input()

    # Prompt user for destination article
    print("\nWhat is the destination article?")
    dest = input()
    print()


# Determine if inputs are valid.
# It's important to note that some Wikipedia articles will redirect immediately. If one of these is the destination, the program will fail.
# I don't have anything set up to combat this, so please make sure that the articles you choose exist before you run them.
try:
    wp = wikiparser.WikiParser(initial)
except:
    print("Given article {0} does not exist.".format(initial))
    exit()

try:
    wp2 = wikiparser.WikiParser(dest)
except:
    print("Given article {0} does not exist.".format(dest))
    exit()


print("Finding fastest path from", initial, "to", dest)
print()

# Call search and note times
tic = time.time()
path = wp.search(dest)
print(" "*get_terminal_size()[0], end="\r")

toc = time.time()

ret = path.pop(0)

# Assemble return string
for x in path:
    ret += " -> " + x

# Final printing
print()
print(ret, "\n")
print("Time taken:", "{:.4f}".format(toc - tic), "seconds")