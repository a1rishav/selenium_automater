# selenium_automater
Python script to automate web app flow, can be used for automated testing, playing a sequence of steps in chrome. It can also download and save the downloaded content to a directory.

## Prerequites
Take a look at setup/setup.txt

## Why?
While testing web apps or buying some stuff over internet in a limited time or consider any web activity, a user interacts in a similar fashion. He clicks, refreshes, types some input, hits submit. So why not write these steps in plain english and let the automater execute the steps.

## How?
Well there is some syntax required for the automator to understand the command, but's its simple.
Let's consider a simple task to type hello world in google search, hit enter and click on images in the results.

```
open google search https://www.google.com/
set search string "hello world" with xpath //INPUT[@class='gLFyf gsfi']
click search with xpath (//INPUT[@value='Google Search'])[2]
click images with xpath //A[@class='q qs'][text()='Images']
```

### Explanation : 

Commands and syntax:
  - open 
    - syntax --> `open` message `url`
    - message can be any string
    - messages make instructions meaningful
  - set 
    - used while entering some input like username, password or search string
    - syntax --> `set` message `keyword_to_be_set` `with` `xpath` `xpath_value`
    - `xpath` can be replaced by `class` or `id`
    - `xpath_value`can be replaced by `class_value` or `id_value`
  - click
    - syntax --> `click` message `with` `xpath` `xpath_value`
    
    
### Configs :

APP_HOME = "/home/rishav/work/pycharmProjects/app_automation" {project home directory}
SCRIPTS_DIR = path.join(APP_HOME, "automater_scripts") {directory to store intruction sequences}

DOWNLOAD_DIR = "downloads" {directory to store downloaded content}
LOGS_DIR = "logs" {directory name to save logs}
DRIVER = 'chromedriver' {driver being used}


### Suggestions :
This plugin helps in knowing the relative xpaths of elements --> https://chrome.google.com/webstore/detail/relative-xpath-helper/eanaofphbanknlngejejepmfomkjaiic

    
      
    
   



