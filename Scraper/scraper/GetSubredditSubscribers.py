import praw

_ua = "u/tooproudtopose reddit-scraper"

class SubredditScraper(object):
    def __init__(self,ua=_ua):
        self.conn = praw.Reddit(user_agent=ua)
        self.authors={}

    def scrapeSubredditUsers(self, target_subreddit, nposts):
        
        r = self.conn
        sub = r.get_subreddit(target_subreddit)
        post_generator = sub.get_new(limit=None)

        n=0
        for post in post_generator:
            n+=1
            try:
                comments = praw.helpers.flatten_tree(post.comments)
            except Exception as e:
                print("Could not store comment due to %s" %e)
            print("Scraped %d posts" % n)
            lc = len(comments)
            nc = 0
            for comment in comments:
                nc +=1
                #print("%d of %d comments scraped") % (nc, lc)
                try:
                    author = comment.author
                    self.authors[author.name] = author
                except:
                    break
            if n >= nposts:
                break
