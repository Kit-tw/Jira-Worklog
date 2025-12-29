# Basic Concept
- create an App that has jira script / can insert jira token
- time base on create branch / manually input
	- Automatic field Example
		- Jira card name = branch name
		- create branch date from "git reflog --date=iso <branch-name> = start worklog date
		- time range is between latest commit and create branch
		- description is commit message 
	- Command for get date
		- git reflog show --date=iso "$(git branch --show-current)"
	- Python
		- Core
			- Store Token as env / file
			- Try Catch With Sheet if fail input for sheet link then store it
				- found : use exist sheet and try catch for template file 
				- not found: use template sheet (store in directory for user didn't have sheet)
			- Input with checkbox "use info from git"
				- info git has commit name, branch, date
				- find way to get jira URL from worklog sheet
				- option insert to google sheet (Default = checked)
			- if insert to jira success insert to sheet with done
				- logic for loop to find date row of worklog date
		- GUI
			- Python Tkinter / ttkbootstrap
			- pyQt
	- Info
		- permission  -> BROWSE_PROJECTS, EDIT_ISSUES
		- API
			- myself for checking authen
			- mypermission for checking edit
# step
1. command to open application ex. worklog
2. Jira account page 
    - have account
    -  option
    - next
        - step 3
    - remove
        - delete json file and go to doesn't have account page
    - doesn't have account
	    - show page
		- how to sign-in and get jira api token
		- get jira site [multiple site ?]
		- store in json file
3. Jira insert project / issue page
	- input 
	    - issue
		- date
		- timestamp
		- list worklog
		- description
	- checkbox : automatic insert
	    - get info from "git reflog show --date=iso "$(git branch --show-current)"
    - checkbox : insert to google sheets
	    - if check
			- get link from store file
		- if no file
			- insert file
 