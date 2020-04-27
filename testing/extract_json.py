import json

def save_links(year):
    fn = "nytimes/" + year + ".json"
    links = []
    with open(fn) as json_file:
        data = json.load(json_file)
        for p in data:
            links.append(p["web_url"])
            if len(links) == 40:
                break

    fn2 = "article_links/" + year + ".txt"

    file1 = open(fn2, "w")
    for line in links:
        file1.write(line)
        file1.write("\n")
    file1.close()

save_links("2001")