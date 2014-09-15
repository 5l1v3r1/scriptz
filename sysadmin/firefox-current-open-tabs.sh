#!/bin/bash
#Source: https://raymii.org/s/snippets/Get_the_current_or_all_Firefox_tab_urls_in_Bash.html
#Description:
#License

#TODO: auto get firefox profile name

python2 <<< $'import json\nf = open("/home/username/.mozilla/firefox/RANDOM.profile/sessionstore.js", "r")\njdata = json.loads(f.read())\nf.close()\nfor win in jdata.get("windows"):\n\tfor tab in win.get("tabs"):\n\t\ti = tab.get("index") - 1\n\t\tprint tab.get("entries")[i].get("url")'
