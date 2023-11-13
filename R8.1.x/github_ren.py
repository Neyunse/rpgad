####
#
# Copyright (c) Neyunse
#
# Thanks to the help: CharlieFuu69
#
# _ren.py files are only supported from renpy 8.1
# But you can copy and paste the imports and class 
# inside the init python block 
########################################################################
# How to use in .rpy
#
# define git_token = "<TOKEN>"
# define git_repo = "<OWNER>/<REPO>"
#
# screen package_dl():
#     vbox:
#       textbutton "Download package" action Show("confirm", message="Would you like to install this package?",yes_action=Show("Download", filename="pa_lang_en.rpa", dl_path="./"), no_action=Return())
#
#
#
# label start:
#     show screen package_dl
#
#
# explanation:
# Screen: Download(filename, dl_path="pakages")
#       - filename: full name of the file in Github Release ex: "pakage_lang.zip"
#       - if dl_path is not provided, the default download folder is pakages. (the folder need exist)
# 
# How to get github token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
####


"""renpy
init python:
"""

import requests, os, threading
class GithubDownload(threading.Thread):
    """
    This class initializes the class with the repo name, the token, and the download path
    
    :param repo: The name of the repository you want to download
    :param token: The token you created in the previous step
    :param dl_path: The path to the directory where you want to download the packages, defaults to
    packages (optional)
    """

    def __init__(self, settings):
        threading.Thread.__init__(self)
        self.repo = settings["git_repo"]
        self.token = settings["git_token"]
        self.path = settings["path"]
        self.git_release_name = settings["git_release_name"]
        self.filename = settings["filename"]

        self.length = 0
        self.dl = 0.0
        self.raw_length = 0
        self.raw_dl = 0.0
        self.percent = 0.0
        self.dl_progress = ""
        self.dl_status = False
        self.dl_error = False
        self.dl_error_message = ""

    def get_releases(self):
        """
        It takes the repo name and the token and returns the latest release of the repo
        """

        url = "https://api.github.com/repos/{}/releases".format(
            self.repo)
        try:
            r = requests.get(url, headers={
                'Authorization': 'Bearer {}'.format(self.token)
            })

            if r.status_code != 200:
                message = r.json()["message"]
                raise Exception(message)

            r_result = r.json()

            filter_result = None
            for obj in r_result:
                if obj["name"] == self.git_release_name:
                    filter_result = obj

            return filter_result

        except Exception as e:
            self.dl_error = True
            self.dl_error_message = str(e)
            print(e)

    def search_in_assets(self):
        """
        It takes a name as an argument, searches for the latest release, then searches for the asset
        with the name that was passed in, and returns the asset
        
        :param name: The name of the asset you want to download
        :return: the result of the get_asset_by_id function.
        """

        try:
            latest = self.get_releases()

            if latest:
                asset_list = latest['assets_url']

                assets = requests.get(asset_list, headers={

                    'Authorization': 'Bearer {}'.format(self.token)
                })

                asset_result = assets.json()

                search_asset = [
                    element for element in asset_result if element['name'] == self.filename]

                id = search_asset[0]["id"]

                return self.get_asset_by_id(id, self.filename)

        except Exception as e:
            print(e)

    def get_asset_by_id(self, id, filename):
        """
        It downloads a file from a url and saves it to a directory.

        :param id: The id of the asset you want to download
        :param filename: The name of the file you want to download
        """
        try:
            url = "https://api.github.com/repos/{}/releases/assets/{}".format(
                self.repo, id)
            base = os.path.normpath(renpy.config.gamedir)

            existSize = 0
            write_type = "wb"
            headers = {}
            if os.path.exists(f"{base}/{self.path}/{filename}"):
                write_type = "ab"
                existSize = os.path.getsize(f"{base}/{self.path}/{filename}")
                headers = {
                    'Content-Type': 'application/octet-stream',
                    'accept': "application/octet-stream",
                    'Range': "bytes=%s-" % (existSize),
                    'Authorization': 'Bearer {}'.format(self.token)
                }
            else:
                headers = {
                    'Content-Type': 'application/octet-stream',
                    'accept': "application/octet-stream",
                    'Authorization': 'Bearer {}'.format(self.token)
                }

            asset = requests.get(
                url,
                headers=headers,
                stream=True

            )

            dl = 0.0

            total_length = int(asset.headers['Content-Length'])

            self.raw_length = total_length

            self.length = round(total_length / 1000, 2)

            with open(f"{base}/{self.path}/{filename}", write_type) as f:
                for chunk in asset.iter_content(chunk_size=1024):

                    dl += len(chunk)
                    self.raw_dl = dl
                    self.dl = round(dl / 1000, 2)
                    self.percent = 100 * (self.dl/self.length)
                    self.dl_progress = "%.02f MB / %.02f MB" % (
                        self.dl, self.length)
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            self.dl_status = False
            self.dl_error_message = True
            self.dl_error_message = ""
        finally:
            self.dl_status = True


    def unit_formatter(self, _bytes):
        """
        It takes a number of bytes and returns a string with the number of bytes formatted to the
        appropriate unit.
        
        :param _bytes: The number of bytes to be formatted
        :return: The return value is a string.
        """
        unit_data = {
            "B": {
                "unit": _bytes < 1024.0,
                "div": 1.0},
            "KB": {
                "unit": all([_bytes >= 1024.0, _bytes < 1048576.0]),
                "div": 1024.0},
            "MB": {
                "unit": all([_bytes >= 1048576.0, _bytes < 1073741824.0]),
                "div": 1048576.0},
            "GB": {
                "unit": _bytes >= 1073741824.0,
                "div": 1073741824.0}
        }

        for i in unit_data:
            if unit_data[i]["unit"]:
                return "%.02f %s" % (float(_bytes) / unit_data[i]["div"], i)

    @property
    def sizelist(self):
        """
        It takes the raw download and file size and converts them into a human readable format
        :return: The current and total size of the file being downloaded.
        """
        current = self.unit_formatter(self.raw_dl)
        total = self.unit_formatter(self.raw_length)
        return [current, total]

    def run(self):
        """
        It searches for a file in the assets folder, and if it doesn't find it, it restarts the
        interaction
        :return: The return value of the function.
        """

        try:
            self.search_in_assets()
        except Exception as e:
            self.dl_error_message = True
            self.dl_error_message = e
            print(e)

