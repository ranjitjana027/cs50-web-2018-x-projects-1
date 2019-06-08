import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine=create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))

def main():
	f=open("books.csv")
	reader=csv.reader(f)
	for isbn, title, author, year in reader:
		db.execute("insert into books(isbn,title,author,year) values (:isbn, :title, :author, :year)",{"isbn":isbn,"title":title,"author":author,"year":year})
		#print(f"Added {title} written by {author}.")
	db.commit()

if __name__=="__main__":
	main()