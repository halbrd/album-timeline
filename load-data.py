import json
from plexapi.server import PlexServer

with open('config.json', 'r') as f:
    config = json.load(f)

plex = PlexServer(config['hostname'], config['token'])

music = plex.library.section('Music')

albums = music.albums()

def album_to_cover_art_url(album):
    # return config['hostname'] + album.thumb + '?X-Plex-Token=' + config['token']
    return config['hostname'] + '/photo/:/transcode?url=' + album.thumb + '&width=100&height=100&X-Plex-Token=' + config['token']

def album_to_html(album):
    name = album.title
    cover_art_url = album_to_cover_art_url(album)
    # return f'<figure><img src="{cover_art_url}" alt="{name}"><figcaption>{name}</figcaption></figure>'
    return f'<img src="{cover_art_url}" alt="{name}">'

def process_album(album):
    if album.originallyAvailableAt is None:
        print(f'WARNING: {album.title} has no release date. It will be excluded from the timeline.')
        return None

    return {
        'content': album_to_html(album),
        'start': album.originallyAvailableAt.strftime('%Y-%m-%d'),
    }

albums = map(process_album, albums)
albums = filter(None.__ne__, albums)
albums = list(albums)
for i in range(len(albums)):
    albums[i]['id'] = i + 1

with open('chart.html', 'r') as f:
    body_lines = f.readlines()

upper_bound = body_lines.index('// meta: start data\n')
lower_bound = body_lines.index('// meta: end data\n')

body_lines = body_lines[:upper_bound + 1] + [json.dumps(albums) + '\n'] + body_lines[lower_bound:]

with open('chart.html', 'w') as f:
    f.writelines(body_lines)
