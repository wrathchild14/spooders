from bs4 import BeautifulSoup, Comment, Tag
import re


def generate_wrapper(html1, html2):
    soup1 = BeautifulSoup(html1, 'html.parser')
    soup2 = BeautifulSoup(html2, 'html.parser')

    unwanted_tags = ["script", "input", "option", "style"]
    for tag in soup1(unwanted_tags):
        tag.decompose()
    for tag in soup2(unwanted_tags):
        tag.decompose()

    head1 = soup1.find("head")
    body1 = soup1.find("body")
    html1_tag = soup1.find("html")
    head2 = soup2.find("head")
    body2 = soup2.find("body")
    html2_tag = soup2.find("html")

    regex = ""
    if head1 and head2:
        regex += generate_regex(head1, head2) + "\n"
    if body1 and body2:
        regex += generate_regex(body1, body2) + "\n"
    if html1_tag and html2_tag:
        regex = "<html>" + regex + "</html>"
        attrs = get_common_attrs(html1_tag, html2_tag)
        if attrs:
            regex = regex[:-1] + attrs + ">"

    regex = '\r\n'.join(line for line in regex.splitlines() if line)
    return regex, None


def generate_regex(tag1, tag2, indent=0):
    attrs = get_common_attrs(tag1, tag2)

    regex = "\n" + " " * indent + "<" + tag1.name + attrs + ">\n"
    for child1, child2 in zip(tag1.children, tag2.children):
        if child1.name and child2.name:
            if isinstance(child1, Comment):
                continue
            elif child1.string:
                if child1.string.strip() == child2.string.strip():
                    regex += " " * (indent + 2) + re.escape(child1.string.strip()).replace("\\", "") + "\n"
                else:
                    regex += " " * (indent + 2) + "#PCDATA"
            elif child1.name == child2.name:
                regex += generate_regex(child1, child2, indent=indent + 2)
            else:
                regex += " " * (indent + 2) + "<" + child1.name + ".*?>.*?</" + child1.name + ">\n"

    regex += "\n" + " " * indent + "</" + tag1.name + ">\n"
    return regex


def get_common_attrs(tag1, tag2):
    attrs1 = tag1.attrs if isinstance(tag1, Tag) else {}
    attrs2 = tag2.attrs if isinstance(tag2, Tag) else {}
    common_attrs = ""
    for key in attrs1.keys():
        if key in attrs2 and str(attrs1[key]) == str(attrs2[key]):
            if key == "style":
                continue
            if "[" not in str(attrs1[key]) and "]" not in str(attrs1[key]):
                common_attrs += f' {key}="{attrs1[key]}"'
    return common_attrs


if __name__ == "__main__":
    # file = open("../webpages/Steam/Euro Truck Simulator 2 on Steam.html",
    #             encoding="utf-8")
    # file = open("../webpages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html",
    #             encoding="utf-8")
    file = open("../webpages/overstock.com/jewelry01.html",
                encoding="windows-1252")
    page_audi = file.read()
    file.close()

    file = open("../webpages/Steam/Save 25_ on This Means Warp on Steam.html",
                encoding="utf-8")
    # file = open("../webpages/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html",
    #             encoding="utf-8")
    file = open("../webpages/overstock.com/jewelry02.html", encoding="windows-1252")
    page_volvo = file.read()
    file.close()

    wrapper_text, wrapper_dict = generate_wrapper(page_audi, page_volvo)
    print(wrapper_text)
