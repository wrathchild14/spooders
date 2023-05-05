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

    some_function(html_1, html_2)


def some_function(wrapper, sample):

    wrapper = html_to_string(str(wrapper))
    sample = html_to_string(str(sample))

    print(wrapper)

    p_w = 0
    p_s = 0

    while True:
        wrapper_tag, wrapper_content = get_tag_w_content(wrapper[p_w])
        sample_tag, sample_content = get_tag_w_content(sample[p_s])

        if "</html" in wrapper_tag:
            break
        if "</html" in sample_tag:
            break

        print(wrapper_tag)
        print(sample_tag)
        # keyboard.read_key()

        if wrapper_tag == sample_tag:
            if sample_content != wrapper_content:
                wrapper[p_w] = wrapper_tag + ">#PCDATA"
        else:
            # Tags don't match so try to find iterators
            # Try to find matching square on sample, assume mismatch on sample

            opening_tag = sample_tag
            closing_index = find_closing_tag_index(opening_tag, sample, p_s)
            square = sample[p_s:closing_index + 1]
            sequence = get_tag_sequence(square)

            p_w_matching = find_sequence_in_html(sequence, wrapper)

            # if len(sequence) == 2:
            #     if find_sequence_in_html(sequence, wrapper) == -1:
            #         print("Is optional sample")
            #     else:

            if p_w_matching == -1:
                print("Out most block is optional on sample, check the rest")
                inner_sequence = sequence[1:]



                p_s = closing_index - 1

            else:
                print("Mismatch on wrapper")
                opening_tag = wrapper_tag
                closing_index = find_closing_tag_index(opening_tag, wrapper, p_w)
                square = wrapper[p_w:closing_index + 1]
                sequence = get_tag_sequence(square)
                print(sequence)
                if len(sequence) == 2:
                    optional = f"({square[0] + square[1]})?"
                    # Remove opening
                    print(wrapper.pop(p_w))
                    # Change closing
                    wrapper[closing_index-1] = optional
                    p_w = closing_index - 1
                    p_s -= 1
                    print(p_w)
                    print(p_s)

        p_w += 1
        p_s += 1
        print(wrapper)


def find_sequence_in_html(sequence, html):
    if len(sequence) == 1:
        temp = [sequence]
    else:
        temp = sequence
    i = 0
    condition = 0
    while i < len(html):
        for t in temp:
            if html[i].startswith(t):
                i += 1
                condition += 1
                if condition == len(temp):
                    print("Found matching sequnce")
                    return i
            else:
                condition = 0
                i += 1
        i += 1
    return -1


def get_tag_sequence(sequence):
    result = []
    for string in sequence:
        tag, x = get_tag_w_content(string)
        result.append(tag)
    return result


def find_closing_tag_index(opening, html, i):
    if ' ' in opening:
        closing = f'</{opening[1:].split()[0]}>'
    else:
        closing = f'</{opening[1:]}>'
    for j in range(i, len(html)):
        content = html[j]
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
    for char in html_string:
        if char == '<':
            if current_tag:
                result.append(current_tag)
                current_tag = ''
            current_tag = char
        elif current_tag:
            current_tag += char
    if current_tag:
        result.append(current_tag)
    return result


run_roadrunner()
