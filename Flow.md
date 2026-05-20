# Basic Concept
- Create an App that has a Jira script/can insert Jira token
- Time based on create branch / manually input
	- Automatic field Example
		- Jira card name = parsed from git branch name using regex (extracts issue key like `WFW-512` from keys like `WFW-512-FIX`, `wfw-512-something`)
		- Create branch date from `git reflog --date=iso <branch-name>` = start worklog date
		- Time range is between latest commit and create branch
		- Description is commit message 
	- Command for get date
		- `git reflog show --date=iso "$(git branch --show-current)"`
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
			- Python CustomTkinter
		- CLI
			- Interactive console mode activated with the `-git` flag
			- Fetches git branch name, parses the issue key, retrieves Jira details, calculates time spent, and prompts user to edit/confirm each field.
	- Info
		- permission  -> BROWSE_PROJECTS, EDIT_ISSUES
		- API
			- myself for checking authen
			- mypermission for checking edit

# Workflow Steps

## GUI Mode (Default)
1. Run application: `python gui.py`
2. Jira account configuration page (requires email, prefix site, and API token).
3. Jira insert project/issue page:
	- Input fields: Issue, Date, Time Spent, Description.
	- Checkbox: "Automate Worklog" using `Git` option (pre-fills values from git branch & reflog).
	- Checkbox: "Insert to sheet" (inserts log row into Google Sheets).

## CLI Mode
1. Run application: `python gui.py -git`
2. Validates stored Jira credentials (aborts if not found/expired).
3. Extracts issue key from git branch (using regex `([A-Za-z][A-Za-z0-9]+-[0-9]+)` normalized to uppercase).
4. Fetches issue details and calculates reflog time/comments.
5. Displays interactive command-line prompts pre-filled with defaults. User can edit or press `[Enter]` to accept.
6. Confirms worklog insertion to Jira.
7. Prompts to sync with Google Sheets (if credentials configured).
8. Logs results and saves to history.

# Recommended Features in the Next Update

1. **CLI Configuration Setup**:
   - Allow setting up Jira credentials and Google Sheets credentials directly from the command line if they are missing or expired (instead of requiring the GUI).
   
2. **Specify Target Directory (`-repo` flag)**:
   - Introduce a `-repo <path>` CLI argument to execute the git extraction logic on any specify directory/repo instead of strictly using the current working directory (`os.getcwd()`).

3. **Dry Run Option (`-dry-run` or `-d`)**:
   - Provide a command-line flag to perform all parsing and API detail fetches, displaying what would be logged without actually posting to Jira or writing to Google Sheets.

4. **Advanced Git Reflog / Commit Range Parsing**:
   - Allow configuring the commit range or branch name source (e.g. `--since`, `--until`, or specifying a different branch to compare against) for more accurate time tracking.

5. **Excluding Weekends/Non-Working Hours**:
   - Improve the git time spent calculation by filtering out weekends and non-working hours to prevent inflated logging times.