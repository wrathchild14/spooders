def clear_JSON(filepath):
    with open(filepath, 'w') as f:
        f.truncate(0)