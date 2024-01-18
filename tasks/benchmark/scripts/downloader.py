#!/usr/bin/python3

import asyncio
import contextvars
import functools
import json
import os
import urllib.parse
import urllib.request
from hashlib import md5

import requests



async def main():
    base_url = "https://raw.githubusercontent.com/t-immanuel/cudnn-installer/main/cudnn-local-repo-ubuntu2004-8.9.7.29_1.0-1_amd64/"
    base_dir = "temp"
    concurrent_download_semaphore = asyncio.Semaphore(5)  # 5 concurrent-downloads

    hash_contents = download_hash_information(base_url, base_dir)
    tasks = []
    for index, hash_content in enumerate(hash_contents):
        index = str(index)
        file_name = os.path.join(base_dir, index)
        url = urllib.parse.urljoin(base_url, index)
        task = asyncio.create_task(download_split(url, file_name, hash_content, concurrent_download_semaphore))
        tasks.append(task)
    await asyncio.gather(*tasks)



def download_hash_information(url, base_dir):
    os.makedirs(base_dir, exist_ok=True)
    url_path = urllib.parse.urljoin(url, "hash")
    hash_file_path = os.path.join(base_dir, "hash")

    if os.path.isfile(hash_file_path):
        with open(hash_file_path) as f:
            return json.load(f)

    content = download_content(url_path)
    with open(hash_file_path, "wb") as f:
        f.write(content)
    return json.loads(content.decode("utf-8"))


async def download_split(url, file_name, expected_md5_hash, sempahore):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    if os.path.isfile(file_name):
        with open(file_name, "rb") as f:
            content = f.read()
        if md5(content).hexdigest() == expected_md5_hash:
            print(f"{file_name} already exists")
            return content

    async with sempahore:
        print(f"Downloading {file_name}...")
        content = await download_content_async(url)
    assert md5(content).hexdigest() == expected_md5_hash
    with open(file_name, "wb") as f:
        f.write(content)
    print(f"Downloaded {file_name}")
    return content


async def download_content_async(url):
    return await to_thread(download_content, url)


def download_content(url):
    return urllib.request.urlopen(url).read()


async def to_thread(func, /, *args, **kwargs):  # substitute for asyncio.to_thread, for older python versions
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)


if __name__ == "__main__":
    asyncio.run(main())
