from downloader import download_video

def process_txt(file_path):
    results = []

    with open(file_path, "r") as f:
        links = f.readlines()

    for link in links:
        link = link.strip()
        if link:
            title, file_path = download_video(link)
            results.append((title, file_path))

    return results
