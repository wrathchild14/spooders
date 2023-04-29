import re
import json
from utils import clear_JSON


def extract_overstock(html_content, json_filename):
    titles = re.findall(r"<td\s+valign=\"top\">\s+<a\s+href=\"\S*\"><b>(.*)</b>", html_content)
    list_prices = re.findall(r"<td\salign=\"left\"\s+nowrap=\"nowrap\"><s>(.*)</s>", html_content)
    prices = re.findall(r"<span\sclass=\"bigred\"><b>(.*)</b>", html_content)
    savings_data = re.findall(r"<span\sclass=\"littleorange\">(.+?)</span>", html_content)
    contents_data = re.findall(r"<span\sclass=\"normal\">(.+?)<br>", html_content, flags=re.DOTALL)

    savings_data = [save for save in savings_data if "<b" not in save]
    savings = []
    saving_percents = []

    for item in savings_data:
        parts = item.split()
        savings.append(parts[0])
        saving_percents.append(parts[1])

    contents = []

    for string in contents_data:
        modified_string = string.replace('\n', ' ')
        contents.append(modified_string)

    # print(titles)
    # print(list_prices)
    # print(prices)
    # print(savings)
    # print(saving_percents)
    # print(contents)

    for i in range(len(titles)):
        item = {
            "title": titles[i],
            "list_price": list_prices[i],
            "price": prices[i],
            "savings": savings[i],
            "saving_percent": saving_percents[i],
            "content": contents[i]
        }

        with open(json_filename, "a", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False, indent=4)
            f.write("\n")


def extract_rtvslo(html_content, json_filename):

    title = re.search(r'<h1>(.*?)</h1>', html_content).group(1)
    published_time = re.search(r"<div class=\"publish-meta\">\s+(.+?)<br>", html_content).group(1)
    author = re.search(r'<div class=\"author-name\">(.+?)</div>', html_content).group(1)
    subtitle = re.search(r'<div class=\"subtitle\">(.+?)</div>', html_content).group(1)
    lead = re.search(r'<p class=\"lead\">(.+?)</p>', html_content).group(1)
    content = re.search(r'<article class="article">\s*(.+?)\s*</article>', html_content, flags=re.DOTALL).group(1)
    text = re.sub('<.*?>', '', content)

    text = text.split("//]]>")[1]
    text = ' '.join(text.split())

    # print("Title:", title)
    # print("Published time:", published_time)
    # print("Author:", author)
    # print("Subtitle:", subtitle)
    # print("Lead:", lead)
    # print("Content:", text)

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


def run_regex():

    websites = [r"../webpages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html",
                r"../webpages/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html",
                r"../webpages/overstock.com/jewelry01.html",
                r"../webpages/overstock.com/jewelry02.html"
                ]

    json_filename = r"../extraction_results/regex_output.json"

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

        else:
            print("Error: Unknown website")


run_regex()