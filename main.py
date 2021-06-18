import time
import sys
import traceback
from scraper import do_scrape, start_thread
# i = 7147442272
if __name__ == "__main__":
    # while True:
    # print("{}: Starting scrape cycle".format(time.ctime()))
    try:
        start_thread()
    except KeyboardInterrupt:
        print("Exiting....")
        sys.exit(1)
    except Exception as exc:
        print("Error with the scraping:", sys.exc_info()[0])
        traceback.print_exc()
        # else:
        #     print("{}: Successfully finished scraping".format(time.ctime()))
        # time.sleep(10)
