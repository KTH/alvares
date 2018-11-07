__author__ = 'tinglev@kth.se'

import json

DEPLOYMENT_STRING = r"""
    {
        "applicationName": "kth-azure-app",
        "cluster": "active",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "slackChannels": "#team-pipeline,#developers",
        "publicNameSwedish": "Monitorapp",
        "publicNameEnglish": "Monitor application",
        "descriptionSwedish": "Monitorapp för klustret",
        "descriptionEnglish": "Monitor application for cluster",
        "monitorPath": "/_monitor",
        "created": "",
        "importance": "high",
        "applicationPath": "/kth-azure-app",
        "detectifyProfileTokens": "abc123xyz456,987mnb654vcx"
    }
"""

ERROR_STRING = r"""
    {
        "message": "An error occured",
        "slackChannels": "#team-pipeline-logs,#ita-ops",
        "stackTrace": "This is a multiline\nstack trace"
    }
"""

def get_deployment():
    global DEPLOYMENT_STRING # pylint: disable=W0603
    return json.loads(DEPLOYMENT_STRING)

def get_error():
    global ERROR_STRING # pylint: disable=W0603
    return json.loads(ERROR_STRING)
