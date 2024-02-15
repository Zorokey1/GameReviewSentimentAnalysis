from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from dotenv import load_dotenv
import MySQLdb
import time



"""
    This function returns a dictionary of the critic reviews from MetaCritic
    @Param webBrowser a Selenium webDriver that dumps the page content to BeautifulSoup
    @Param gameURL the unique slug that every game has on MetaCritic
    @Return a dictionary of the reviews
"""
def getReviewData(webBrowser, gameURL):
    webBrowser.get(f"https://www.metacritic.com/game/{gameURL}/critic-reviews/")
    webBrowser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(1) # Waits so that the website can load all of the reviews
    soup = bs(webBrowser.page_source, features="lxml")

    scrapedData = []

    # Finds all of the green scores based off of the class of the div container
    greenScores = soup.find_all(
        "div",
        class_="c-siteReviewScore u-flexbox-column u-flexbox-alignCenter u-flexbox-justifyCenter g-text-bold c-siteReviewScore_green g-color-gray90 c-siteReviewScore_medium",
    )

    # Finds all of the yellow scores based off of the class of the div container
    yellowScores = soup.find_all(
        "div",
        class_="c-siteReviewScore u-flexbox-column u-flexbox-alignCenter u-flexbox-justifyCenter g-text-bold c-siteReviewScore_yellow g-color-gray90 c-siteReviewScore_medium",
    )

    # Finds all of the red scores based off of the class of the div container
    redScores = soup.find_all(
        "div",
        class_="c-siteReviewScore u-flexbox-column u-flexbox-alignCenter u-flexbox-justifyCenter g-text-bold c-siteReviewScore_red g-color-white c-siteReviewScore_medium",
    )

    # Concats all of the scores into one list
    # Very important that it is in this order as reviews are ordered top to bottom
    scores = greenScores + yellowScores + redScores

    reviews = soup.find_all(
        "div", class_="c-siteReview_quote g-outer-spacing-bottom-small"
    )

    publicationTags = soup.find_all(
        "a", class_="c-siteReviewHeader_publicationName g-text-bold g-color-gray90"
    )

    for review, score, publication in zip(reviews, scores, publicationTags):
        scrapedData.append(
            {
                "publication": publication[
                    "title"
                ],  # Gets the publication of the review
                "review": review.string,  # Gets the review content
                "score": score["title"].split(" ")[
                    1
                ],  # Gets the score by splitting the string 'Metascore 90 out of 100'
            }
        )

    return scrapedData


"""
    Gets the game urls from the browse list
    @Param webBrowser the selenium web browser
    @Param pageNumber page number for the catalog of games
    @Return a dictionary with a unique id and a formatted game url
    
"""
def getGameURLS(webBrowser, pageNumber):
    webBrowser.get(
        f"https://www.metacritic.com/browse/game/?releaseYearMin=1958&releaseYearMax=2023&page={pageNumber}"
    )
    soup = bs(webBrowser.page_source, features="lxml")

    index2Game = {}

    """
        Cleans a game string and turns it into a slug
        @Param gameString the name of the game
        @Return a string that represents the propper slug
    """

    def cleanGameString(gameString):
        cleanGameSlug = (
            gameString.string.lower()
            .replace("'", "")
            .replace(":", "")
            .replace(" - ", "-")
            .replace("- ", "-")
            .replace(" -", "-")
            .replace(" / ", " ")
            .replace("/", " ")
            .replace(" ", "-")
            .replace("(", "")
            .replace(")", "")
            .replace(".", "")
            .replace("&", "and")
            .replace(",", "")
            .replace(";", "")
            .replace("--", "-")
        )
        if cleanGameSlug[-1] == "-":
            cleanGameSlug = cleanGameSlug[:-1]
        return cleanGameSlug

    for uncleanGame in soup.find_all("h3", class_="c-finderProductCard_titleHeading"):
        game = uncleanGame.contents  # All of the children of the h3 tag

        index2Game[game[0].string.replace(".", "")] = {"gameName": game[2].string, "gameSlug": cleanGameString(game[2])}

    return index2Game



'''
    Scrapes the data and puts it into a database for a single page of the metacritic browse
    @Param browser selenium webdriver
    @Param myCursor a connection to the database that is used to execute SQL
    @Param pageIndex the desired page that will be scraped
'''
def scrapeData(browser, myCursor, pageIndex):
    
    startTime = time.time()
    gameDict = getGameURLS(browser, pageIndex)

    for gameIndex in gameDict.keys():
        gameStartTime = time.time()
        reviews = getReviewData(browser, gameDict[gameIndex]["gameSlug"])
        
        for review in reviews:
            gameName = gameDict[gameIndex]['gameName']
            publication = review['publication']
            individualReview = review['review']
            score = review["score"]
            myCursor.execute("INSERT INTO Reviews (Game, Website, Review, Score) VALUES (%s, %s, %s, %s)", (gameName, publication, individualReview, score))
        gameEndTime = time.time()
        
        if len(reviews) == 0:
            print(f"    No Reviews for {gameDict[gameIndex]['gameName']} can be found, Incorrect Slug: {gameDict[gameIndex]['gameSlug']}")
        else:
            print(f"    Game Completed: {gameDict[gameIndex]['gameName']}, Time Taken: {gameEndTime-gameStartTime}")

    myCursor.execute("COMMIT")
    endTime = time.time()
    print(f"Page number: {pageIndex}, Time Taken: {endTime-startTime}")

chromeOptions = Options()

chromeOptions.add_argument("enable-automation")
chromeOptions.add_argument("--window-size=1920,1080")
chromeOptions.add_argument("--no-sandbox")
chromeOptions.add_argument("--disable-extensions")
chromeOptions.add_argument("--dns-prefetch-disable")
chromeOptions.add_argument("--disable-gpu")

browser = webdriver.Chrome(options=chromeOptions)

load_dotenv()
Password = os.getenv('PASSWORD')

db = MySQLdb.connect(
    host="localhost", user="root", passwd=Password, database="reviewData"
)

myCursor = db.cursor()

multPageStartTime = time.time()


for pageNumber in range(528, 545):
    print(f"Current Page Number: {pageNumber}")
    scrapeData(browser, myCursor, pageNumber)
    

print(f"Total time is: {time.time()-multPageStartTime}")

myCursor.execute("SELECT * FROM Reviews")
print(myCursor.fetchall())

print("done")
