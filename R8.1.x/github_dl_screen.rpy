init python:
    config.per_frame_screens.append("Download")

# uncomment this defines and configure your token and repo
#call screen downloader(settings={
#        "git_repo": "", # User/repo
#        "git_token": "",
#        "path": "packages",
#        "filename": "",
#        "git_release_name": ""
#    })

screen Download(settings={}):
    zorder 49000
    modal True
    default dl = GithubDownload(settings["git_repo"], settings["git_token"], settings["filename"], settings["path"])
    on "show" action Function(dl.start)

    if dl.dl_status:
        frame:
            background "gui/main_menu.png"
            xfill True
            yfill True
            padding (10,10,10,10)
            xalign .5
            yalign .5
            vbox:
                xalign .5
                yalign .5
                frame:
                    padding (10,10,10,10)
                    has vbox
                    text "Download Complete!" xalign .5
                    textbutton "Restart the game" action Function(renpy.quit, relaunch = True, status = 0, save = False) xalign .5
    else:
        frame:
            background "gui/main_menu.png"
            xfill True
            yfill True
 
                
            vbox:
                yfill True
                frame:
                    yalign 1.0
                    vbox:
                        spacing 2
                        
                        text "[[%.02f%%] - %s / %s - [filename]" % (dl.percent, dl.sizelist[0], dl.sizelist[1])
                        bar value AnimatedValue(dl.percent, 100.0)
 
