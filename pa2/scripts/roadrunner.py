from bs4 import BeautifulSoup, Tag, NavigableString, Comment, Doctype
import re
import keyboard








def filter_webpage(webpage):

    # Remove all newline characters
    for tag in webpage.find_all(string=lambda text: isinstance(text, NavigableString)):
        tag.replace_with(tag.replace("\n", ""))

    for doctype in webpage.find_all(string=lambda text: isinstance(text, Doctype)):
        doctype.extract()


    # Remove all trailing and leading whitespace
    for tag in webpage.find_all(string=lambda text: isinstance(text, NavigableString)):
        tag.replace_with(tag.strip())

    return webpage


def run_roadrunner():
    websites = [r"../webpages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html",
                    r"../webpages/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html",
                    r"../webpages/overstock.com/jewelry01.html",
                    r"../webpages/overstock.com/jewelry02.html",
                    r"../webpages/Samples/sample1.html",
                    r"../webpages/Samples/sample2.html"
                    ]

    with open(websites[4], encoding="utf-8") as file:
        html_1 = BeautifulSoup(file.read(), "lxml")

    with open(websites[5], encoding="utf-8") as file:
        html_2 = BeautifulSoup(file.read(), "lxml")

    html_1 = filter_webpage(html_1)
    html_2 = filter_webpage(html_2)

    # run(html_1, html_2)
    # print(html_1)

    tags = html_1.find_all()
    # for tag in tags:
    #     print(tag.name)


    some_function(html_1, html_2)


def some_function(wrapper, sample):

    # Wrapper is the one that is the longest
    # n_t1 = len(wrapper.find_all())
    # n_t2 = len(sample.find_all())
    #
    # if n_t2 > n_t1:
    #     temp = wrapper
    #     wrapper = sample
    #     sample = temp
    #
    # tags_w = wrapper.find_all()
    # tags_s = sample.find_all()
    #
    # i = 0
    #
    # while i < len(tags_w) and i < len(tags_s):
    #     if tags_w[i].name == tags_s[i].name:
    #         if tags_w[i].string is not None and tags_s[i].string is not None:
    #             if tags_w[i].string != tags_s[i].string:
    #                 tags_w[i].string = "#PCDATA"
    #     else:
    #         # Tags don't match so try to find iterators
    #         # Find terminal in sample
    #
    #         print("Mismatch")
    # i += 1
    #
    # print(wrapper)
    #
    # # Create an array to store the tags


    wrapper = html_to_string(str(wrapper))
    sample = html_to_string(str(sample))

    print(wrapper)
    i = 0
    while i < len(wrapper) and i < len(sample):
        wrapper_tag, wrapper_content = get_tag_w_content(wrapper[i])
        sample_tag, sample_content = get_tag_w_content(sample[i])
        if wrapper_tag == sample_tag:
            if sample_content != wrapper_content:
                wrapper[i] = wrapper_tag + ">#PCDATA"
        else:
            # Tags don't match so try to find iterators
            # Find closing
            if sample[i] == "</html>":
                print("Smo na konc")

            # Find square
            opening = sample_tag
            closing_index = find_closing(opening, sample, i)
            if closing_index != -1:
                print("Closing found!")
                square = sample[i:closing_index+1]

                print(square)
                break


        i += 1

    print(wrapper)



def find_closing(opening, sample, i):
    closing = f'</{opening[1:]}>'
    for j in range(i, len(sample)):
        content = sample[j]
        if closing == content:
            # Return index
            return j
    return -1




def get_tag_w_content(string):
    tag = ''
    content = ''
    for s in string:
        # if s == '>':
        #     break
        if s == ' ' or s == '>':
            # Get reminder of text as content
            content = string[string.index(s) + 1:]
            break
        tag += s
    # print(content)
    return tag, content


def html_to_string(html_string):
    result = []
    current_tag = ''

    # Loop through the characters in the HTML string
    for char in html_string:
        # Check if the current character is the opening angle bracket for a tag
        if char == '<':
            # If we have a current tag, append it to the result list
            if current_tag:
                result.append(current_tag)
                current_tag = ''
            # Start building a new tag
            current_tag = char
        # If we're in the middle of building a tag, append the current character
        elif current_tag:
            current_tag += char

    # Append the last tag to the result list
    if current_tag:
        result.append(current_tag)

    # Print the result
    return result

run_roadrunner()

# for tag_w, tag_s in zip(tags_w, tags_s):
#     if tag_w.string is not None:
#         if tag_w.string != tag_s.string:
#             # Insert #PCADATA
#             pass


# # Get all squares of a webpage
# children = [el for el in html_1.descendants]
#
#
# appender=[]
# for child in children:
#     if not isinstance(child, str):
#         appender.append(child)
#
#
# # Get all squares of a webpage
# children2 = [el for el in html_2.descendants]
# appender2=[]
# for child in children2:
#     if not isinstance(child, str):
#         appender2.append(child)
#
# with open(websites[4], encoding="utf-8") as file:
#     soup = BeautifulSoup(file.read(), "lxml")
#
# tags = soup.find_all()
# for tag in tags:
#     print(tag.name)
#     if tag.string is not None:
#         print(tag.string)


# for c in children:
#     keyboard.read_key()
#     print(c.getText())

# for x, y in zip(appender, appender2):
#     keyboard.read_key()
#
#
#     if x == y:
#         print(x)
#     else:
#         print(x)
#         print(y)
