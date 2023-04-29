import sys
from regex import run_regex


if __name__ == "__main__":
    if sys.argv[1] == "A":
        print("Regular expressions extraction")
        run_regex()
    elif sys.argv[1] == "B":
        print("XPath extraction")
        # TODO: add XPath extraction
    elif sys.argv[1] == "C":
        print("Automatic Web extraction")
        # TODO: add automatic web extraction
    else:
        print("No extractor selected!")
