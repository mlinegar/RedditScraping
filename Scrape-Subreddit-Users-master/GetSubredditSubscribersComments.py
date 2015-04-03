# NOTES
#
#  * Should add associated subreddit to user entry. 
#  * Users should get inserted as they're scraped. Maybe use database
#    to hold users instead of a dict? Or enter users into db as they're
#    entered in the dict

import database as db
#from ScrapeSubUsers import *
from GetSubredditSubscribers import *
import time
import praw

starttime = time.time()

_nposts = 1


db.init_db()
s = SubredditScraper()


start = time.time()

s.scrapeSubredditUsers(nposts=_nposts)
end = time.time()

print("Time elapsed to scrape %d posts: %d seconds" % (_nposts, int(end-start)))
print("# Unique subreddit users found: %d" % len(s.authors))

session = Session()

for username in s.authors:
    try:
        session.add(User(username))
    except err:
        # TODO: determine exact SQLAlchemy error thrown here
        print("could not save user %s: %s" % (username, err))

session.commit()

from sqlalchemy import distinct
allusers = session.query(User.username)
scraped = session.query(distinct(Comment.author))
unscraped = [user for user in allusers if user not in scraped]
# create a function for the try/except, then run the try block on the function
# add getting comments into the scraper

r=praw.Reddit(user_agent="u/tooproudtopose reddit-scraper")

for username in unscraped:
    basename = '%s.user.csv' % username
    full_path = '/Users/mlinegar/Documents/LDA/Usertext/%s' % fname
    start = time.time()
    comments = r.get_redditor(username).get_comments(limit=None)
    lc = 0

    with open(full_path, "w") as f:
        writer = csv.writer(f, lineterminator = "\n")

        for comment in comments:
            writer.writerow((comment.body, comment.author, datetime.datetime.fromtimestamp(comment.created_utc)))
            lc += 1
            db_comment = Comment(comment)
            try:
                session.add(db_comment)
            except e:
                print("could not write comment to db: %s" % e)

    end = time.time()

    print( "        %d:%d - %s: %d comments downloaded in %d seconds." % (end.tm_hour, end.tm_min, username, lc, int(end-start)))
