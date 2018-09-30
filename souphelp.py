import requests
from bs4 import BeautifulSoup


class Soup(object):

    def __init__(self):
        self.base_uri = "https://tekstovi.net/"
        self.base_artist = "https://tekstovi.net/2,{},0.html"

    def get_artists(self, c):
        artists = []
        url = self.base_artist.format(c)
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        for p in soup.find_all("p", {"class": "artLyrList"}):
            href = str(p.a.get('href'))
            id = int(href.split(',')[1])
            artists.append({
                "id": id,
                "url": self.base_uri + href,
                "name": p.a.text
            })
        return artists

    def get_songs(self, a):
        songs = []
        soup = BeautifulSoup(requests.get(a["url"]).text, "html.parser")
        for p in soup.find_all("p", {"class": "artLyrList"}):
            href = str(p.a.get('href'))
            id = int(href.split(',')[2].split('.')[0])
            songs.append({
                "id": id,
                "artist_id": a["id"],
                "url": self.base_uri + href,
                "name": p.a.text
            })
        return songs

    def get_lyric(self, s):
        soup = BeautifulSoup(requests.get(s["url"]).text, "html.parser")
        p = soup.find("p", {"class": "lyric"})
        return p.text
