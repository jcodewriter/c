import requests
from requests.exceptions import Timeout
import threading
import time
from bs4 import BeautifulSoup
from mysql.connector import MySQLConnection, Error
from mysql_connect import connect

pos = 7152077422
thread_limit = []


def start_thread():
    print("{}: Starting scrape cycle".format(time.ctime()))
    global pos, thread_limit
    thread_limit = []
    threads = []

    for i in range(0, 40):
        thread_handler = threading.Thread(
            target=do_scrape, args=((pos+50*i), (pos+50*(i+1)),))
        threads.append(thread_handler)
        thread_handler.start()

    for i in threads:
        i.join()

    thread_limit.sort()
    if thread_limit == []:
        pos += 2000
    else:
        pos = thread_limit[0]
    # finish scrape
    print("{}: Successfully finished scraping".format(time.ctime()))

    time.sleep(10)
    # restart thread
    start_thread()


def do_scrape(s_pos, e_pos):
    global thread_limit
    loop_condition = True
    sfbay_areas = ['eby', 'nby', 'pen', 'sfc', 'scz', 'sby']

    for i in range(s_pos, e_pos):
        for k in range(0, len(sfbay_areas)):
            url = 'https://sfbay.craigslist.org/' + \
                sfbay_areas[k]+'/cto/'+str(i)+'.html'
            soup = get_request(url)
            if soup == False or soup == None:
                if soup == False:
                    loop_condition = False
                    thread_limit.append(i)
                    break
                else:
                    continue
            else:
                make_data(soup, url, i, "sfbay", sfbay_areas[k])
                break
        if loop_condition == False:
            break


def get_request(url):
    try:
        res = requests.get(url, timeout=1)
    except requests.ConnectionError as e:
        print("ERROR", e)
        return None
    except Timeout:
        print('The request timed out')
        return None

    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "html.parser")
        print("Found Page", url, res.status_code)
        return soup
    else:
        soup = BeautifulSoup(res.content, "html.parser")
        err_page = soup.select("h1.post-not-found-heading")
        print("Not Found Page", url, res.status_code)
        if err_page != []:
            return False


def make_data(soup, url, post_id, area, subarea):
    title_selector = soup.select("span#titletextonly")
    title = title_selector[0].get_text()

    price_selector = soup.select("span.price")
    price = (price_selector[0].get_text()).lstrip("$")

    hood_selector = soup.select("span.postingtitletext small")
    if hood_selector == []:
        hood = None
    else:
        hood = hood_selector[0].get_text()

    image_selector = soup.select(".slide.first.visible img")
    if image_selector == []:
        image = None
    else:
        image = image_selector[0].get("src")

    time_selector = soup.select("time.date.timeago")
    post_time = time_selector[0].get("datetime")

    if len(time_selector) > 2:
        last_update = time_selector[2].get("datetime")
    else:
        last_update = None

    data = {"post_id": post_id, "area_name": area, "subarea_name": subarea, "title": title, "url": url, "img_src": image,
            "post_time": post_time, "last_update": last_update, "price": price, "hood": hood}
    attr_data = {}
    attrgroup_selector = soup.select("p.attrgroup")[1]
    attrgroup = attrgroup_selector.find_all("span")
    for i in range(0, len(attrgroup)):
        attrgroup_str = attrgroup[i].get_text()
        attr = attrgroup_str.split(":")
        attr_data[attr[0]] = attr[1].lstrip()

    if "odometer" in attr_data:
        data["odometer"] = attr_data["odometer"]
    else:
        data["odometer"] = None

    if "condition" in attr_data:
        data["cond"] = attr_data["condition"]
    else:
        data["cond"] = None

    if "cylinders" in attr_data:
        data["cylinders"] = attr_data["cylinders"]
    else:
        data["cylinders"] = None

    if "drive" in attr_data:
        data["drive"] = attr_data["drive"]
    else:
        data["drive"] = None

    if "fuel" in attr_data:
        data["fuel"] = attr_data["fuel"]
    else:
        data["fuel"] = None

    if "paint color" in attr_data:
        data["paint_color"] = attr_data["paint color"]
    else:
        data["paint_color"] = None

    if "size" in attr_data:
        data["size"] = attr_data["size"]
    else:
        data["size"] = None

    if "transmission" in attr_data:
        data["transmission"] = attr_data["transmission"]
    else:
        data["transmission"] = None

    if "type" in attr_data:
        data["tp"] = attr_data["type"]
    else:
        data["tp"] = None

    if "title status" in attr_data:
        data["title_status"] = attr_data["title status"]
    else:
        data["title_status"] = None

    insert_cta(data)


def insert_cta(data):
    sql = "REPLACE INTO car_trucks(post_id,area_name,subarea_name,name,url,img_src,hood,price,post_time,last_update,cond,cylinders,drive,fuel,paint_color,size,transmission,tp,title_status,odometer) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (data['post_id'], data['area_name'], data['subarea_name'], data['title'], data['url'],
           data['img_src'], data['hood'], data['price'], data['post_time'], data['last_update'], data['cond'], data['cylinders'], data['drive'], data['fuel'], data['paint_color'], data['size'], data['transmission'], data['tp'], data['title_status'], data['odometer'])

    try:
        cursor = connect.cursor()
        cursor.execute(sql, val)
        cursor.close()
    except Error as e:
        print('error:', e)
