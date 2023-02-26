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
# define git_repo = "Neyunse/Silent-Love"
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

    def __init__(self, repo, token, filename ,dl_path):
        super(GithubDownload, self).__init__()

        """
        This function initializes the class with the repo name, the token, and the download path
        
        :param repo: The name of the repository you want to download
        :param token: The token you created in the previous step
        :param dl_path: The path to the directory where you want to download the packages, defaults to
        packages (optional)
        """

        self.repo = repo
        self.token = token
        self.path = dl_path
        self.filename = filename

        
        self.length = 0
        self.dl = 0.0
        self.raw_length = 0
        self.raw_dl = 0.0
        self.percent = 0.0
        self.dl_progress = ""
        self.dl_status = False

    def get_latest_releases(self):
        """
        It takes the repo name and the token and returns the latest release of the repo
        """
        
        url = "https://api.github.com/repos/{}/releases/latest".format(
            self.repo)
        try:
            r = requests.get(url, headers={
                'Authorization': 'Bearer {}'.format(self.token)
            })

            result = r.json()

            return result

        except Exception as e:
            print(e)
        finally:
            
            renpy.restart_interaction()

    def search_in_assets(self):
        """
        It takes a name as an argument, searches for the latest release, then searches for the asset
        with the name that was passed in, and returns the asset
        
        :param name: The name of the asset you want to download
        :return: the result of the get_asset_by_id function.
        """
       
        try:
            latest = self.get_latest_releases()

            asset_list = latest['assets_url']

            assets = requests.get(asset_list, headers={
                
                'Authorization': 'Bearer {}'.format(self.token)
            })

            asset_result = assets.json()

            search_asset = [element for element in asset_result if element['name'] == self.filename]

            id = search_asset[0]["id"]

        
            return self.get_asset_by_id(id, self.filename)

        except Exception as e:
            print(e)
        finally:
            
            renpy.restart_interaction()

    def get_asset_by_id(self, id, filename):
        """
        It downloads a file from a url and saves it to a directory.

        :param id: The id of the asset you want to download
        :param filename: The name of the file you want to download
        """
        try:
            url = "https://api.github.com/repos/{}/releases/assets/{}".format(
            self.repo, id)
            asset = requests.get(url, headers={
                'Content-Type': 'application/octet-stream',
                'accept': "application/octet-stream",
                'Authorization': 'Bearer {}'.format(self.token)
            }, stream=True)

            base = os.path.normpath(config.gamedir)
            outfile = open(base+'/{}/{}'.format(self.path,filename), 'wb')
            outfile.write(asset.content)
            

            dl = 0.0

            total_length = int(asset.headers['Content-Length'])

            self.raw_length = total_length

            self.length = round(total_length / 1000, 2)


            for data in asset.iter_content(chunk_size=4096):
                dl += len(data)
                self.raw_dl = dl
                self.dl = round(dl / 1000, 2)
                self.percent = 100 * (self.dl/self.length)
                self.dl_progress = "%.02f MB / %.02f MB" % (self.dl, self.length)
                self.dl_status = False
                
             
                 
            if self.dl >= self.length:
                outfile.close()
                asset.close()
            
        except Exception as e:
            print(e)
        finally:
            self.dl_status = True
            renpy.restart_interaction()
 
    def unit_formatter(self, _bytes):
        """
        It takes a number of bytes and returns a string with the number of bytes formatted to the
        appropriate unit.
        
        :param _bytes: The number of bytes to be formatted
        :return: The return value is a string.
        """
        unit_data = {
                    "B" : {
                            "unit" : _bytes < 1000,
                            "div" : 1},
                    "KB" : {
                            "unit" : all([_bytes >= 1000, _bytes < 1000000]),
                            "div" : 1000},
                    "MB" : {
                            "unit" : all([_bytes >= 1000000, _bytes < 1000000000]),
                            "div" : 1000000},
                    "GB" : {
                            "unit" : _bytes >= 1000000000,
                            "div" : 1000000000}
                    }
 
        for i in unit_data:
            if unit_data[i]["unit"]:
                result = _bytes / unit_data[i]["div"]
                return "%.02f %s" % (result, i)

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
            return self.search_in_assets()
        except Exception as e:
                print(e)
        finally:
            
            renpy.restart_interaction()
