import os.path
import sys
import warnings


def main():
    if len(sys.argv) <= 1:
        raise ValueError("Require 1 argument: path of file/folder to be converted to LF end-of-line")
    rootdir = sys.argv[1]

    if os.path.isfile(rootdir):
        convert_to_LF_EOL(rootdir)
        return
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            file_full_path = os.path.join(subdir, file)
            convert_to_LF_EOL(file_full_path)


TEXTCHARS = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})


def is_binary_string(string: bytes):
    return bool(string.translate(None, TEXTCHARS))


def is_binary_file(file_path: str, read_block_size=10 * 1024 * 1024):
    with open(file_path, "rb") as f:
        content = f.read()
    print(f"Converting 1: {file_path} {len(content)}")

    with open(file_path, "rb") as f:
        while True:
            content = f.read(read_block_size)
            if is_binary_string(content):
                return True
            if content == b'':
                break
    return False


def convert_to_LF_EOL(file_path: str):
    assert os.path.isfile(file_path)
    if is_binary_file(file_path):
        warnings.warn(f"\n Skipping... Detected as a binary file: {file_path} \n", stacklevel=2)
        return
    with open(file_path, "rb") as f:
        f.seek(0)
        content = f.read()
        f.close()

    for i in range(3):
        print(f"Converting 2-{i}: {file_path} {len(content)}")
        with open(file_path, "rb") as f:
            f.seek(0)
            content = f.read()
            f.close()
        if len(content) != 0:
            break

    print(f"Converting 3: {file_path} {len(content)}")
    content = content.replace(b"\r\n", b"\n")

    with open(file_path, "wb") as f:
        f.write(content)
    print(f"Converted: {file_path} {len(content)}")


if __name__ == "__main__":
    main()
