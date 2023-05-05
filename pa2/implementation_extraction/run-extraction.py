import sys
from regex import run_regex
from XPath import run_xpath
from roadrunner import run_roadrunner

if __name__ == "__main__":
    if sys.argv[1] == "A":
        print("Regular expressions extraction")
        run_regex()
    elif sys.argv[1] == "B":
        print("XPath extraction")
        run_xpath()
    elif sys.argv[1] == "C":
        print("Automatic Web extraction")
        # can be rtvslo, steam, ovestock
        run_roadrunner("steam")
    else:
        print("No extractor selected!")
