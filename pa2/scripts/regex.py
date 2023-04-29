import re
import json



def extract_rtvslo(html_content):

    title = re.search(r'<h1>(.*?)</h1>', html_content).group(1)
    published_time = re.search(r"<div class=\"publish-meta\">\s+(.+?)<br>", html_content).group(1)
    author = re.search(r'<div class=\"author-name\">(.+?)</div>', html_content).group(1)
    subtitle = re.search(r'<div class=\"subtitle\">(.+?)</div>', html_content).group(1)
    lead = re.search(r'<p class=\"lead\">(.+?)</p>', html_content).group(1)
    content = re.search(r'<article class="article">\s*(.+?)\s*</article>', html_content, flags=re.DOTALL).group(1)
    text = re.sub('<.*?>', '', content)

    text = text.split("//]]>")[1]
    text = ' '.join(text.split())

    print("Title:", title)
    print("Published time:", published_time)
    print("Author:", author)
    print("Subtitle:", subtitle)
    print("Lead:", lead)
    print("Content:", text)

    data = {
        "title": title,
        "published_time": published_time,
        "author": author,
        "subtitle": subtitle,
        "lead": lead,
        "content": text
    }


    filename = r"../extraction_results/regex_output.json"
    # Save the data to a JSON file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def run_regex():

    file = open(r"../webpages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html", encoding='utf-8')
    content = file.read()
    extract_rtvslo(content)
    file.close()


run_regex()