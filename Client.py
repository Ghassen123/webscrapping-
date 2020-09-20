import zmq
import requests
from bs4 import BeautifulSoup
import json
import time,datetime
ports=[5556]


def get_products_urls_for_all_category(index_url):
    """
    get the list of all product by category from web site index
    :param index_url:
    :return: product_category_url_list
    """
    # Step 1: Sending a HTTP request to a index_url
    try:
        reqs = requests.get(index_url)
        # Step 2: Parse the html content
        soup = BeautifulSoup(reqs.text, 'lxml')
    except Exception as Ex:
        with open('error_log_file.json', 'a') as outfile:
            json.dump({"exception_text": str(Ex), "url": index_url, "methode": "get_products_urls_for_all_category"}, outfile)
            outfile.write("\n")
        pass

    # Step 3: init empty list to store all products category urls
    product_category_url_list = []
    try:
        # Step 4: Analyze the HTML tag to extract products category urls
        for tag in soup.find_all('div', {'id': "onglet_nav_1"}):
            products = tag.find_all("ul")[0]
            lis = products.find_all("li")
            for li in lis:
                product_category_url_list.append(li.a.get('href'))
    except Exception as ex:
        print('report url execption')
        with open('error_log_file.json', 'a') as outfile:
            json.dump({"exception_text":str(ex),"url":index_url,"methode":"get_products_urls_for_all_category"}, outfile)
            outfile.write("\n")
        pass
    print(product_category_url_list)

    return list(dict.fromkeys(product_category_url_list))


def get_urls_list_for_each_category(categ_url):
    """
    get list of all product en a given category
    :param categ_url:
    :return: all_products_urls_by_category
    """
    # Step 1: Sending a HTTP request to a categ_url
    try:
        reqs = requests.get(categ_url)
        # Step 2: Parse the html content
        soup = BeautifulSoup(reqs.text, 'lxml')
    except Exception as Ex:
        with open('error_log_file.json', 'a') as outfile:
            json.dump({"exception_text": str(Ex), "url": categ_url, "methode": "get_urls_list_for_each_category"}, outfile)
            outfile.write("\n")
            pass

    # Step 3: init empty list to store all products urls by category
    all_products_urls_by_category = []
    try:
        # Step 4: Analyze the HTML tag to extract urls for given  category
        for tag in soup.find_all('div', {'id': "boutiqueV2"}):
            products = tag.find_all("ul")[0]
            lis = products.find_all("li")
            for li in lis:
                all_products_urls_by_category.append(li.a.get('href'))
    except Exception as ex:
        print('report url execption')
        with open('error_log_file.json', 'a') as outfile:
            json.dump({"exception_text":str(ex),"url":categ_url,"methode":"get_urls_list_for_each_category"}, outfile)
            outfile.write("\n")
        pass
    return list(dict.fromkeys(all_products_urls_by_category))


def get_final_url_product(s_url):
    """
    extract final product url in which we can get the product info
    from list of all products web page
    :return:
    """
    # Step 1: Sending a HTTP request to a index_url
    try:
        reqs = requests.get(s_url)
        # Step 2: Parse the html content
        soup = BeautifulSoup(reqs.text, 'lxml')
    except Exception as Ex:
        print('report url execption')
        with open('error_log_file.json', 'a') as outfile:
            json.dump({"exception_text": str(Ex), "url": s_url, "methode": "get_urls_list_for_each_category"}, outfile)
            outfile.write("\n")
            pass
    final_product_urls_list = []
    try:
        # Step 3: Analyze the HTML tag to extract final url form list of all products
        for tag in soup.find_all('div', attrs={'class': "col-xs-6"}):
            for i in tag.find_all("a"):
                if i.get('href') and "https://" in i.get('href'):
                    final_product_urls_list.append(i.get('href'))
    except Exception as ex:
        print('report url execption')
        with open('error_log_file.json', 'a') as outfile:
            json.dump({"exception_text":str(ex),"url":s_url,"methode":"get_final_url_product"}, outfile)
            outfile.write("\n")
        pass
    #to make sure that there is no dublications
    print(list(dict.fromkeys(final_product_urls_list)))
    return list(dict.fromkeys(final_product_urls_list))

def get_products_list_urls_form_index(index_url):
    """
    get list of all products url after scraping index web page and get all products category urls
    then for each category get the url of every product and finally get the product info
    :param index_url: web site index url houra.fr
    :return: products_url_list
    """
    start_time = time.time()
    st = str(datetime.datetime.now())

    product_category_url_list = get_products_urls_for_all_category(index_url)
    all_products_url = []
    final_urls_list = []

    for url in product_category_url_list:
        all_products_url += get_urls_list_for_each_category(url)
    for url_ in all_products_url:
        res = get_final_url_product(url_)
        final_urls_list += res
        # save products url in txt file
    with open("product_urls.txt", "a") as products:
        [products.write(str(p) + "\n") for p in list(dict.fromkeys(final_urls_list))]

    report_info =dict(
    Start_Time =  st,
    End_Time = str(datetime.datetime.now()),
    Processing_Time_Seconds = str((time.time() - start_time)),
    Status = "Success",
    Methode="get_products_list_urls_form_index")
    with open("report_file.txt", "a") as reportfile:
        json.dump(report_info, reportfile)
        reportfile.write("\n")
    return list(dict.fromkeys(final_urls_list))



def get_product_info_from_client(index_url):
    product_list_urls = get_products_list_urls_form_index(index_url)
    # with open("./product_urls.txt", "r") as f:
    #     product_list_urls = f.read().splitlines()
    start_time = time.time()
    st = str(datetime.datetime.now())
    for url in product_list_urls:
        print("Connecting to worker…")
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://localhost:{ports[0]}")

        print("Sending request %s …" % url)
        socket.send_string(url)

        #  Get the reply.
        message = json.loads(socket.recv())
        print("Received reply  [ %s ]" % (message))
        with open('output.json','a') as outfile:
            if message:
                data={}
                data[str(message["Product"])]=message
                json.dump(data,outfile)
                outfile.write("\n")
    report_info =dict(
    Start_Time =  str(st),
    End_Time = str(datetime.datetime.now()),
    Processing_Time_Seconds = str((time.time() - start_time)),
    Status = "Success",
    Methode="get_product_info_from_client")
    with open("report_file.txt", "a") as reportfile:
        json.dump(report_info, reportfile)
        reportfile.write("\n")
    return "Scraping Completed successfully"


index_url="https://www.houra.fr/"
get_product_info_from_client(index_url)