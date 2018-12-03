# selenium_automater
Python script to automate web app flow, can be used for automated testing, playing a sequence of steps in chrome

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

The command `open` has the following syntax :
open message url



