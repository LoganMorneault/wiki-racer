from requests import get
from bs4 import BeautifulSoup
from queue import PriorityQueue
from os import get_terminal_size


# The bulk of my code. I've written well over 2000 lines of code for this project, but a lot of it was bad and has been scrapped.
class WikiParser:
    def __init__(self, article=""):
        self.title = article.replace(" ", "_") # String
        self.url = "http://en.wikipedia.org/wiki/" + self.title # String
        self.links = self.processLinks() # set of String
        self.linksCleaned = False

    # Calling cleanLinks twice would normally erase all links, since none start with /wiki/ after the first runthrough. To combat this, I made a field to track if cleanLinks has been called.
    def cleanLinks(self):
        if not self.linksCleaned:
            self.linksCleaned = True

            newLinks = set()

            for link in self.links:
                if link.startswith('/wiki/'):
                    link = link[6:]
                    if "(identifier)" not in link and "Category:" not in link and "Help:" not in link and "Template:" not in link and "Template_talk:" not in link and "Special:" not in link and "File:" not in link and "(disambiguation)" not in link and "List" not in link and "Wikipedia:" not in link and "Portal:" not in link:
                        newLinks.add(link)

            self.links = newLinks
        

    # Tried multiprocessing here but I gave up because I didn't think it was worth it.
    def processLinks(self):
        html = get(self.url)

        if not html:
            raise Exception("Article \"{0}\" does not exist".format(self.title))

        soup = BeautifulSoup(html.content, "html.parser")
        content = soup.find('div', {'id':'bodyContent'})

        links = set()
        
        for a in content.find_all('a'):
            if "href" in a.attrs:
                link = str(a.attrs['href'])

                # For our purposes, all valid links must lead back to Wikipedia
                if link.startswith("/wiki/"):
                    links.add(link)

        return links


    # Returns a priority queue of each article in self.links, weighted by how many linked articles they have in common with the target article.

    # target is a sorted list of links
    def getPQbyOverlap(self, targetArticle, targetLinks, explored=set(), fromPath = [], ):
        # The goal here is to determine which of my articles has the most overlap with the destination article
        ret = []   

        if targetArticle in self.links:
            fromPath.append(targetArticle)
            return fromPath

        linkList = list(self.links.difference(explored))
        linkList.sort()

        '''
        To convert this to multiprocessing/multithreading, I need a function that takes a single article as input but that still has knowledge about the following:
            - targetLinks
            - targetArticle
            - fromPath
        
        Because linkList is a subset of self.links and we know target is not in self.links, target is not in linkList.

        There's a StackOverflow link in wiki-race.py that should be useful for this, but I don't have the time to troubleshoot it for now.
        '''


        # Iterate through the links of this article
        for x in linkList:

            # If we haven't seen this link before
            #if x not in explored:
                if x == targetArticle:
                    fromPath.append(x)
                    return fromPath


                # Clears the terminal so we can get a sense of how much progress we've made without printing hundreds of lines.
                # This is taken directly from a GeeksForGeeks article.
                print(" "*get_terminal_size()[0], end="\r")
                print("Processing " + x, end="\r")



                # Create a WP for x
                wp = WikiParser(x)
                wp.cleanLinks()

                # If the article is directly accessible from this new article's links, return the path.
                # This differs from the usual, so steps should be take nwhen calling getPQbyOverlaps to handle it.
                if targetArticle in wp.links:
                    fromPath.append(x)
                    fromPath.append(targetArticle)
                    return fromPath
                         
                # Determine priority and append to ret
                priority = len(wp.links.intersection(targetLinks))
                ret.append((- priority, (x, fromPath)))

        # Convert ret to PQ and return
        PQ = PriorityQueue()
        for y in ret:
            PQ.put(y)

        return PQ


    # I've decided that I don't necessarily need the shortest path. I just need the fastest path. To accomplish this, I add any unexplored articles to the frontier as soon as the option presents itself.
    def search(self, target:str, hard_stop_point:int=10000):


        # If the target article is this article, return the path.
        if target == self.title:
            return [self.title]
        
        # Process target and clean self.links
        targetPretty = target[:]
        target = target.replace(" ", "_")
        self.cleanLinks()

        

         # We don't want any repeats, so we load the frontier with any link we already know about
        explored = {self.title}.union(self.links)


        # If the target is in the immediate links of the initial article, we're good here too
        if target in explored:  
            return [self.title, target] 

        targetWP = WikiParser(target)
        targetWP.cleanLinks() 

        # Initialize frontiers
        frontier = self.getPQbyOverlap(targetArticle= target, targetLinks=targetWP.links, fromPath=[self.title])

        if type(frontier) == list:
            return frontier

        print(" "*get_terminal_size()[0], end="\r")
        print("There are", frontier.qsize(), "articles accessible from the initial article", "\n")

        # At some point, we want the program to terminate, even if we don't have an answer. I've arbitrarily chosen 10,000 articles to be the default stopping point, but you can do this whenever.
        while len(explored) < hard_stop_point:

            # While the frontier isn't empty, take an item article from it
            while frontier.qsize() != 0:
                article = frontier.get()
                explored.add(article[1][0])

                # Article[0] = priority
                # article[1][0] = title
                # article[1][1] = path
                if article[1][0] == target:
                    article[1][1].append(target)
                    return article[1][1]
                
                # This article isn't the right one. Let's get its links according to our measure function
                wp = WikiParser(article[1][0])
                wp.cleanLinks()

                if target in wp.links:
                    article[1][1].append(target)
                    return article[1][1]

                article[1][1].append(article[1][0])
                tempPQ = wp.getPQbyOverlap(target, targetWP.links, explored, fromPath=article[1][1])

                if type(tempPQ) == list:
                    return tempPQ
                
                # We need to process this data a bit
                # Iterate through ret
                # tempPQ should never contain the target article
                while tempPQ.qsize() != 0:

                    # X is the article's priority
                    # Y is the article's title
                    # z is the article's path
                    x, (y, z) = tempPQ.get()


                    # We have no interest in anything already explored
                    if y not in explored:
                        
                        # If y isn't explored, add it to the list
                        # Also add it to the next frontier
                        explored.add(y)
                        frontier.put((x,(y,z)))