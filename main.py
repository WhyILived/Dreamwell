from extract import search
from scraper import scrape

if __name__ == "__main__":
    res = scrape()
    print(res)
    ans = search(res[0])
    print(ans)