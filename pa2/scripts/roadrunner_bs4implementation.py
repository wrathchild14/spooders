from bs4 import BeautifulSoup, Comment
import re


def generate_wrapper(html1, html2):
    soup1 = BeautifulSoup(html1, 'html.parser')
    soup2 = BeautifulSoup(html2, 'html.parser')
    unwanted_tags = ["script", "input", "option", "style"]
    for tag in soup1(unwanted_tags):
        tag.decompose()
    for tag in soup2(unwanted_tags):
        tag.decompose()

    tags1 = set([tag.name for tag in soup1.find_all()])
    tags2 = set([tag.name for tag in soup2.find_all()])
    common_tags = list(tags1.intersection(tags2))

    regexes = {}
    for tag in common_tags:
        regexes[tag] = generate_regex(tag, soup1, soup2)

    for tag in common_tags:
        regexes[tag] = refine_regex(tag, regexes[tag])

    wrapper = ""
    for tag in common_tags:
        wrapper += regexes[tag] + "\n"
    return wrapper, regexes


def generate_regex(tag, soup1, soup2, indent=0):
    tag1 = soup1.find(tag)
    tag2 = soup2.find(tag)
    attrs = get_common_attrs(tag1, tag2)

    if tag == 'div' and 'id' in tag1.attrs and 'class' in tag1.attrs and tag1.attrs['id'] == 'fb-root' \
            and tag1.attrs['class'] == ['fb_reset']:
        return ''

    regex = " " * indent + "<" + tag + attrs + ">\n"
    if not tag1.contents:
        return ""

    for child in tag1.contents:
        if isinstance(child, Comment):
            continue
        if child.name:
            regex += generate_regex(child.name, soup1, soup2, indent + 2)
        else:
            regex += " " * (indent + 2) + re.escape(str(child).strip()).replace("\\", "") + "\n"

    regex += " " * indent + "</" + tag + ">\n"
    return "\n".join([line for line in regex.split("\n") if line.strip()])


def get_common_attrs(tag1, tag2):
    attrs1 = tag1.attrs
    attrs2 = tag2.attrs
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

    data1 = extract_data(page_audi, wrapper_dict)
    print("Data from page 1:", data1)

    data2 = extract_data(page_volvo, wrapper_dict)
    print("Data from page 2:", data2)
