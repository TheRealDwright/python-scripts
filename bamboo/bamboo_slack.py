#!/usr/bin/python

import sys
import requests
import json
import argparse

from urllib2 import Request, urlopen, URLError, HTTPError

#change this
hook_url = 'https://hooks.slack.com/services/something/somewhat'
#change this
bamboo_api_url = 'http://bamboo.example.com/rest/api/latest/result/'

def main(args):

    print 'setting up build results for %s' % (args.aws_key)

    r = requests.get(bamboo_api_url + args.aws_key + '.json')
    j = requests.get(bamboo_api_url + args.plan_key + '.json?expand=jiraIssues')
    build_state = r.json()['buildState']
    build_plan = r.json()['plan']['name']

    if build_state == 'Successful':
        color = 'good'
        title = 'OK'
    elif build_state != 'Successful':
        color = 'danger'
        title = 'ERROR'

    all_jira_issues = ' '

    if j.json()['jiraIssues']['size'] > 0:
        issues = j.json()['jiraIssues']['issue']
        for jira in issues:
          for key in iter(jira):
            jira_issues = jira[key]
            all_jira_issues += ' %s, ' % (jira_issues)


    elif j.json()['jiraIssues']['size'] == 0:
        all_jira_issues = "There are no Jira Issues Associated with This Build  "

    slack_message = {
        'channel': args.channel,
        'username': 'Bamboo Notifications',
        'icon_url': 'https://qatestingtools.com/sites/default/files/tools_shortcuts/Bamboo%20150.png',
        'text': '%s' % (r.json()['projectName']),
        'attachments': [
            {
                "fallback": title,
                "color": color,
                "text": 'Build Result is %s' % (title) ,
                "fields": [
                    {
                        "short": True,
                        "title": 'Build Plan',
                        "value": '%s with result of %s' % (build_plan, build_state)
                    },
                    {
                        "short": True,
                        "title": 'Reason Started',
                        "value": '%s' % (r.json()['reasonSummary'])
                    },
                    {
                        "short": True,
                        "title": 'Build Time',
                        "value": 'Build ran for %s' % (r.json()['buildDurationDescription'])
                    },
                    {
                        "short": True,
                        "title": 'Build Link',
                        "value": '%s' % (r.json()['plan']['link']['href'])
                    },
                    {
                        "short": False,
                        "title": 'Jira Issues Deployed',
                        'value': '%s' % (all_jira_issues[:-2])
                    }
                ]
            }

        ]
    }
    request = Request(hook_url, json.dumps(slack_message))

    try:
        response = urlopen(request)
        response.read()
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--aws-key', help='bamboo build url in json')
    parser.add_argument('--plan-key', help='URL for plan for Jira Issues')
    parser.add_argument('--channel', help='slack channel for post')
    args = parser.parse_args()
    main(args)
