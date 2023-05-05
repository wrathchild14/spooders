def clear_JSON(filepath):
    with open(filepath, 'w') as f:
        f.truncate(0)


def read_webpage(webpage):
    file = open(webpage, encoding="utf-8")
    result = file.read()
    file.close()
    return result
