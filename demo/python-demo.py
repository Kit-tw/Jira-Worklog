import re
regex = ["df-wcf.atlassian.net","https:/df-wcf.atlassian.net/","https://df-wcf.atlassian.net/","http://df-wcf.atlassian.net/","df-wcf"]
pattern = r'^(?:https?:\/?\/?)?([a-zA-Z0-9-]+)(?:\.atlassian\.net)?\/?$'
for p in regex:
    match = re.match(pattern, p)
    if match:
        print(match.group(1))
