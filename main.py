from bs4 import BeautifulSoup
import requests
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Accepts user input. Format needs to be adhered to otherwise it'll throw an error
year = input("Enter the year: (YYYY-MM-DD)")
url = f"https://www.billboard.com/charts/hot-100/{year}"

response = requests.get(url=url)
website = response.text

SPOTIPY_REDIRECT = "http://example.com"

scope = "playlist-modify-private"

soup = BeautifulSoup(website, "html.parser")

# Gets the songs and artists. The #1 artist data seems to be stored in a different class than the other 99.
first_title = soup.find(name="h3",
                        class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet")
top_titles = soup.find_all(name="h3",
                           class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only")

top_100_list = [re.sub(r"[\n\t]*", "", first_title.get_text())]
for titles in top_titles:
    top_100_list.append(re.sub(r"[\n\t]*", "", titles.get_text()))

first_artist = soup.find(name="span",
                         class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only u-font-size-20@tablet")

top_artists = soup.find_all(name="span",
                            class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only")

top_artists_list = [re.sub(r"[\n\t]*", "", first_artist.get_text())]
for artists in top_artists:
    top_artists_list.append(re.sub(r"[\n\t]*", "", artists.get_text()))


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, cache_path="token.txt"))
user_id = sp.current_user()["id"]
spotipy_uris = []

for i in range(0, 100):
    result = sp.search(q=f"track:{top_100_list[i]} artist:{top_artists_list[i]}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        spotipy_uris.append(uri)
    except IndexError:
        print("Song isn't on Spotify.")

playlist = sp.user_playlist_create(user=user_id, name=f"Top 100 Generated Playlist {year}", public=False, description="The docs ain't great")
playlist_id = playlist["id"]

sp.playlist_add_items(playlist_id=playlist_id, items=spotipy_uris)