import MySQLdb
import os
from dotenv import load_dotenv
import csv

load_dotenv()

Password = os.getenv('PASSWORD')

db = MySQLdb.connect(
    host="localhost", user="root", passwd=Password, database="reviewData"
)


myCursor = db.cursor()

'''
myCursor.execute("UPDATE Reviews SET Review = REPLACE (Review, CHAR(13), '')")
myCursor.execute("Commit")
'''
myCursor.execute("SELECT * FROM tempTable")
rows = myCursor.fetchall()
fp = open('./data/reviews.csv', 'w', encoding='utf-8')
myFile = csv.writer(fp, delimiter=',')
myFile.writerow(['ID', 'Game', 'Website', 'Review', 'Score'])
myFile.writerows(rows)
fp.close()


# myCursor.execute("DROP TABLE Reviews")
# myCursor.execute("CREATE TABLE Reviews(ReviewID int NOT NULL AUTO_INCREMENT, Game varchar(500), Website varchar(100), Review varchar(15000), Score int, PRIMARY KEY (ReviewID))")

# Database Format: Reviews(ReviewID int NOT NULL AUTO_INCREMENT, Game varchar(500), Website varchar(100), Review varchar(15000), Score int, PRIMARY KEY (ReviewID))
