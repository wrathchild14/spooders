from bs4 import BeautifulSoup, Comment, NavigableString, Tag
import re


def generate_wrapper(html1, html2):
    soup1 = BeautifulSoup(html1, 'html.parser')
    soup2 = BeautifulSoup(html2, 'html.parser')
    unwanted_tags = ["script", "input", "option", "style"]
    for tag in soup1(unwanted_tags):
        tag.decompose()
    for tag in soup2(unwanted_tags):
        tag.decompose()

    tags1 = soup1.find_all()
    tags2 = soup2.find_all()

    regex = ""
    for i, (tag1, tag2) in enumerate(zip(tags1, tags2)):
        if tag1.name and tag2.name:
            if isinstance(tag1, Comment):
                continue
            elif tag1.name != tag2.name:
                regex += "<" + tag1.name + ".*?>.*?</" + tag1.name + ">\n"
            else:
                regex += "<" + tag1.name + get_common_attrs(tag1, tag2) + ">\n"
                if tag1.string and tag1.string.strip():
                    regex += re.escape(tag1.string.strip()) + "\n"
                elif tag1.contents:
                    regex += generate_regex(tag1, tag2, indent=2)
                regex += "</" + tag1.name + ">\n"

    return regex, None


def generate_regex(tag1, tag2, indent=0):
    attrs = get_common_attrs(tag1, tag2)

    if attrs is None:
        attrs = ""
    if tag1.name:
        regex = " " * indent + "<" + tag1.name + attrs + ">\n"
        for child1, child2 in zip(tag1.children, tag2.children):
            if child1.name and child2.name:
                if isinstance(child1, Comment):
                    continue
                elif isinstance(child1, str) and child1.strip():
                    regex += " " * (indent + 2) + re.escape(child1.strip()).replace("\\", "") + "\n"
                # elif isinstance(child1, NavigableString) and child1.string.strip():
                #     regex += " " * (indent + 2) + re.escape(child1.string.strip()).replace("\\", "") + "\n"
                elif child1.name == child2.name:
                    regex += generate_regex(child1, child2, indent=indent + 2)
                else:
                    regex += " " * (indent + 2) + "<" + child1.name + ".*?>.*?</" + child1.name + ">\n"

        regex += " " * indent + "</" + tag1.name + ">\n"
        return "\n".join([line for line in regex.split("\n") if line.strip()])
    else:
        return ""


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


# only capture rows with more than one data cell
def refine_regex(tag, regex):
    if tag == "table":
        regex = regex.replace("<tr>", "(<tr>.+?<td>.+?</td>.+?</tr>)")
        regex = regex.replace("<td>", "")
        regex = regex.replace("</td>", "")
        regex = regex.replace("<th>", "")
        regex = regex.replace("</th>", "")
    return regex


def extract_data(page, wrapper):
    soup = BeautifulSoup(page, 'html.parser')
    data = {}
    for tag, regex in wrapper.items():
        matches = re.findall(regex, str(soup))
        if matches:
            data[tag] = matches[0]
    return data


if __name__ == "__main__":
    file = open("../webpages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html",
                encoding="utf-8")
    # file = open("../webpages/overstock.com/jewelry01.html",
    #             encoding="windows-1252")
    page_audi = file.read()
    file.close()

    file = open("../webpages/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html",
                encoding="utf-8")
    # file = open("../webpages/overstock.com/jewelry02.html", encoding="windows-1252")
    page_volvo = file.read()
    file.close()

    wrapper_text, wrapper_dict = generate_wrapper(page_audi, page_volvo)
    print(wrapper_text)

    # data1 = extract_data(page_audi, wrapper_dict)
    # print("Data from page 1:", data1)
    #
    # data2 = extract_data(page_volvo, wrapper_dict)
    # print("Data from page 2:", data2)
