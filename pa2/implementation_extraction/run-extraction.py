import sys
from regex import run_regex
from XPath import run_xpath
from roadrunner import run_roadrunner

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("specify an extraction method")
    else:
        if sys.argv[1] == "A":
            print("Regular expressions extraction")
            run_regex()
        elif sys.argv[1] == "B":
            print("XPath extraction")
            run_xpath()
        elif sys.argv[1] == "C":
            print("Automatic Web extraction")
            keyword = "steam"
            if len(sys.argv) > 2:
                keyword = sys.argv[2]
            run_roadrunner(keyword)
        else:
            print("No extractor selected!")
