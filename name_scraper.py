import requests
from bs4 import BeautifulSoup


def grab_names(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    playerlist = []
    for player in soup.find_all("a", {"class": "ut"}):
        playerlist.append(player.text.replace("\n", ""))

    next_url = soup.find_all("a", {"class": "page-link"})[-1]['href']

    return next_url, playerlist


def write_playernames(num_pages, filename):
    # grab names for 3 pages and use the next url to find the next page
    aggregate_playerlist = []
    url = r'https://jstris.jezevec10.com/sprint?lines=40L&page=1'
    for i in range(num_pages):
        url, playerlist = grab_names(url)
        aggregate_playerlist.extend(playerlist)

    with open(filename, "wb") as f:
        f.write("\n".join(aggregate_playerlist).encode('ascii', 'ignore'))

    return aggregate_playerlist
