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

# myCursor.execute("SELECT * FROM Reviews")
# print(myCursor.fetchall())

myCursor.execute("DROP TABLE Reviews")
myCursor.execute("CREATE TABLE Reviews(ReviewID int NOT NULL AUTO_INCREMENT, Game varchar(500), Website varchar(100), Review varchar(15000), Score int, PRIMARY KEY (ReviewID))")

# Database Format: Reviews(ReviewID int NOT NULL AUTO_INCREMENT, Game varchar(500), Website varchar(100), Review varchar(15000), Score int, PRIMARY KEY (ReviewID))
