import os
from file_utils import read_file_lines, write_output
from diff_engine import compare_files, format_output


DATA_DIR = "data"
OUTPUT_DIR = "output"


def main():

    old_file = os.path.join(DATA_DIR, "old.txt")
    new_file = os.path.join(DATA_DIR, "new.txt")
    output_file = os.path.join(OUTPUT_DIR, "result.txt")

    print("Loading files...")

    old_lines = read_file_lines(old_file)
    new_lines = read_file_lines(new_file)

    print("Comparing files...")

    added, removed, modified = compare_files(old_lines, new_lines)

    result = format_output(added, removed, modified)

    write_output(output_file, result)

    print("\nComparison complete.")
    print(f"Output saved to: {output_file}")


if __name__ == "__main__":
    main()