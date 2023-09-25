import sys
import os
import pyclip as pyperclip
import qbittorrentapi
from dotenv import dotenv_values

# import environment:
# conda env create -f .\environment.yml
# use:
# conda run --live-stream -n qBittorrentBulkApp python main.py

# export existing environment:
# conda env export > <environment-name>.yml

def init():
    init_env_var = dotenv_values()
    init_client = qbittorrentapi.Client(
        host=init_env_var['HOST'],
        port=init_env_var['PORT'],
        username=init_env_var['USERNAME'],
        password=init_env_var['PASSWORD']
    )
    try:
        init_client.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)

    return init_client, init_env_var


def torrent_file_handles(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.torrent'):
            file_path = os.path.join(folder_path, filename)
            yield open(file_path, 'rb')


if __name__ == '__main__':
    client, envVar = init()
    folder_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    torrent_files = torrent_file_handles(folder_path)
    save_paths = []
    # for each ask for a path to save the torrent to, default is current clipboard contents
    for torrent_file in torrent_files:
        clipboard_contents = pyperclip.paste()
        save_path = input(f'Enter save path for {torrent_file.name} ({clipboard_contents}): ') or clipboard_contents
        save_paths.append(save_path)

    # ask for category with default
    category = input(f'\nEnter category ({envVar["CATEGORY"]}): ') or envVar['CATEGORY']

    content_layout_dict = {'1': 'Original', '2': 'Subfolder', '3': 'NoSubfolder'}
    user_input = input(f'\nEnter content layout\n1. Original\n2. Subfolder\n3. NoSubfolder\n(Default is {envVar["CONTENT_LAYOUT"]}): ')
    content_layout_choice = content_layout_dict.get(user_input, envVar['CONTENT_LAYOUT'])

    # upload each torrent file using torrents_add()
    for torrent_file, save_path in zip(torrent_file_handles(folder_path), save_paths):
        client.torrents_add(torrent_files=torrent_file, save_path=save_path, category=category, content_layout=content_layout_choice, is_paused=envVar['IS_PAUSED'])

    for torrent_file in torrent_file_handles(folder_path):
        torrent_file.close()

