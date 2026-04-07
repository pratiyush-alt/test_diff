def read_file_lines(file_path):
    """
    Reads a text file and returns a list of lines
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()


def write_output(file_path, content):
    """
    Writes output string to a file
    """
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)