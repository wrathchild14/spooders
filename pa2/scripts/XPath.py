import json
from lxml import html
from utils import clear_JSON

def extract_steam(html_content, json_filename):
    tree = html.fromstring(html_content)

    game_title = tree.xpath(r"//*[@id='appHubAppName'] [@class='apphub_AppName']/text()")
    review = tree.xpath("//span[@class='game_review_summary positive'] [@itemprop='description']/text()")
    amount_of_reviews = tree.xpath(r"//meta[@itemprop='reviewCount']/@content")
    release_date = tree.xpath(r"//div[@class='date']/text()")
    price = tree.xpath(r"//div[@class='discount_final_price']/text()")
    tags = tree.xpath(r"//div[@class='label']/text()")

    # print(game_title)
    # print(review)
    # print(amount_of_reviews)
    # print(release_date)
    # print(price)
    # print(tags)

    data = {
        "game title": game_title[0],
        "release date": release_date[0],
        "rating": review[0],
        "amount of reviews": amount_of_reviews[0],
        "price": price[0],
        "tags": [t for t in tags]
    }

    with open(json_filename, "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")

    print(json.dumps(data, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False))


def extract_overstock(html_content, json_filename):

    tree = html.fromstring(html_content)

    titles = tree.xpath(r"//*[@valign='top']/a[@href]/b/text()")
    list_prices = tree.xpath(r"//*[@nowrap='nowrap']/s/text()")
    prices = tree.xpath(r"//*[@class='bigred']/b/text()")
    savings_data = tree.xpath(r"//*[@class='littleorange']/text()")
    contents_data = tree.xpath(r"//*[@class='normal']/text()")

    savings = []
    savings_percents = []

    # Dollars and percent are together so we have to split
    for saving in savings_data:
        parts = saving.split(' (')
        savings.append(parts[0])
        savings_percents.append(parts[1].rstrip(')'))

    contents = []

    # We only remove newline with space
    for string in contents_data:
        modified_string = string.replace('\n', ' ')
        contents.append(modified_string)

    # print(titles)
    # print(list_prices)
    # print(prices)
    # print(savings)
    # print(savings_percents)
    # print(contents)

    for i in range(len(titles)):
        item = {
            "title": titles[i],
            "list_price": list_prices[i],
            "price": prices[i],
            "savings": savings[i],
            "saving_percent": savings_percents[i],
            "content": contents[i]
        }

        with open(json_filename, "a", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False, indent=4)
            f.write("\n")

        print(json.dumps(item, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False))


def extract_rtvslo(html_content, json_filename):

    tree = html.fromstring(html_content)

    title = tree.xpath('//h1/text()')[0]
    published_time = tree.xpath("//*[@class='publish-meta']/text()")[0]
    published_time = published_time.lstrip('\t\n\n')
    author = tree.xpath("//*[@class='author-name']/text()")[0]
    subtitle = tree.xpath("//*[@class='subtitle']/text()")[0]
    lead = tree.xpath("//*[@class='lead']/text()")[0]
    contents = tree.xpath("//*[@class='article-body']/article/p/text()|//*[@class='article-body']/article/p/strong/text()")
    text = ' '.join(contents)

    # print(title)
    # print(published_time)
    # print(author)
    # print(subtitle)
    # print(lead)
    # print(text)

    data = {
        "title": title,
        "published_time": published_time,
        "author": author,
        "subtitle": subtitle,
        "lead": lead,
        "content": text
    }

    with open(json_filename, "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")

    print(json.dumps(data, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False))


def run_xpath():
    websites = [r"../webpages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html",
                r"../webpages/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html",
                r"../webpages/overstock.com/jewelry01.html",
                r"../webpages/overstock.com/jewelry02.html",
                r"../webpages/Steam/Euro Truck Simulator 2 on Steam.htm",
                r"../webpages/Steam/Save 25_ on This Means Warp on Steam.htm"
                ]

    websites = [r"../webpages/Steam/Euro Truck Simulator 2 on Steam.htm",
                r"../webpages/Steam/Save 25_ on This Means Warp on Steam.htm"]

    json_filename = r"../extraction_results/XPath_output.json"

    # Clear JSON before writing
    clear_JSON(json_filename)

    for website in websites:

        if "rtvslo" in website:
            file = open(website, encoding="utf-8")
            content = file.read()
            extract_rtvslo(content, json_filename)
            file.close()

        elif "overstock" in website:
            file = open(website)
            content = file.read()
            extract_overstock(content, json_filename)
            file.close()

        elif "Steam" in website:
            file = open(website, encoding="utf-8")
            content = file.read()
            extract_steam(content, json_filename)
            file.close()

        else:
            print("Error: Unknown website")

run_xpath()