from difflib import SequenceMatcher


def compare_files(old_lines, new_lines):

    matcher = SequenceMatcher(None, old_lines, new_lines)

    added = []
    removed = []
    modified = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "insert":
            for idx, line in enumerate(new_lines[j1:j2], start=j1 + 1):
                added.append((idx, line.strip()))

        elif tag == "delete":
            for idx, line in enumerate(old_lines[i1:i2], start=i1 + 1):
                removed.append((idx, line.strip()))

        elif tag == "replace":

            old_block = old_lines[i1:i2]
            new_block = new_lines[j1:j2]

            max_len = max(len(old_block), len(new_block))

            for k in range(max_len):

                old_line = old_block[k].strip() if k < len(old_block) else ""
                new_line = new_block[k].strip() if k < len(new_block) else ""

                modified.append((i1 + k + 1, old_line, new_line))

    return added, removed, modified


def format_output(added, removed, modified):

    result = []

    result.append("FILE COMPARISON RESULT\n")
    result.append("=" * 40 + "\n")

    result.append("\nADDED LINES\n")
    result.append("-" * 20 + "\n")

    if added:
        for line_no, text in added:
            result.append(f"Line {line_no}: {text}\n")
    else:
        result.append("None\n")

    result.append("\nREMOVED LINES\n")
    result.append("-" * 20 + "\n")

    if removed:
        for line_no, text in removed:
            result.append(f"Line {line_no}: {text}\n")
    else:
        result.append("None\n")

    result.append("\nMODIFIED LINES\n")
    result.append("-" * 20 + "\n")

    if modified:
        for line_no, old, new in modified:
            result.append(f"Line {line_no}\n")
            result.append(f"OLD → {old}\n")
            result.append(f"NEW → {new}\n\n")
    else:
        result.append("None\n")

    return "".join(result)