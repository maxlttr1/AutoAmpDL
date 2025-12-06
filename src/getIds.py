from pathlib import Path

dir = Path('/home/maxlttr/mountedDisk/syncthing/music/AutoAmpDL/')
ids = []

for file in dir.iterdir():
    if file.is_file:
        ids.append(file.name.split('[')[1].split(']')[0])

with open('ids.txt', 'w') as f:
    for id in ids:
        f.write("youtube " + id + "\n")