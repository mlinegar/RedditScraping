# NOTES
#
#  * Should add associated subreddit to user entry. 
#  * Users should get inserted as they're scraped. Maybe use database
#    to hold users instead of a dict? Or enter users into db as they're
#    entered in the dict

import time
import csv
import datetime

from sqlalchemy.orm import Session

import praw
from sqlalchemy import distinct

from scraper.GetSubredditSubscribers import SubredditScraper
from scraper.datamodel import User, Comment, init_db
import scraper.database as db

_nposts = 5
starttime = time.time()

init_db()
s = SubredditScraper()


start = time.time()

s.scrapeSubredditUsers(nposts=_nposts)
end = time.time()

print("Time elapsed to scrape %d posts: %d seconds" % (_nposts, int(end-start)))
print("# Unique subreddit users found: %d" % len(s.authors))

session = Session() # Aaaaaand this -- RMD

for username in s.authors:
    try:
        found_users = session.query(User).filter(User.username == username).count()
        if found_users:
            pass
        else:
            session.add(User(username))
            session.commit()
    except Exception as err:
        # TODO: determine exact SQLAlchemy error thrown here
        print("could not save user %s: %s" % (username, err))

session = Session()

allusers = session.query(User.username).all()
scraped = session.query(distinct(Comment.author)).all()
unscraped = [user for user in allusers if user not in scraped]
# create a function for the try/except, then run the try block on the function
# add getting comments into the scraper

r=praw.Reddit(user_agent="u/tooproudtopose reddit-scraper")

for result in unscraped:
    username = result[0]
    basename = '%s.user.csv' % username
    full_path = '/Users/mlinegar/Data/LDA/Usertext/%s' % basename
    start = time.time()
    comments = []

    try:
        comments = r.get_redditor(username).get_comments(limit=100)
    except Exception as e:
        print("Could not find user %s" %result)

    lc = 0

    with open(full_path, "wb") as f:
        writer = csv.writer(f, lineterminator = "\n")

        for comment in comments:
            writer.writerow((comment.body, comment.author, comment.subreddit.display_name, datetime.datetime.fromtimestamp(comment.created_utc)))
            lc += 1
            db_comment = Comment(comment)
            try:
                session.add(db_comment)
                session.commit()
            except Exception as e:
                print("could not write comment to db: %s" % e)

    end = time.time()

    print( "        %s: %d comments downloaded in %d seconds." % (username, lc, int(end-start)))