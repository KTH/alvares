__author__ = 'tinglev@kth.se'

import json
from modules import deployment_enricher

DEPLOYMENT_SAMPLES_WITH_EXPECTED_VALUES = [
    r"""
    {
        "applicationName": "kth-azure-app",
        "cluster": "active",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "created": "",
        "applicationPath": "/my-app",
        "monitorPattern": "APPLICATION_STATUS: OK",
        
        "mock-expected": {
            "monitorUrl" : "https://app.kth.se/my-app/_monitor",
            "applicationUrl" : "https://app.kth.se/my-app",
            "friendlyName": "kth-azure-app",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "low"
        }

    }""",
    r"""
        {
        "applicationName": "kth-azure-app",
        "cluster": "stage",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "created": "",
        "applicationPath": "/my-app",
        
        "mock-expected": {
            "monitorUrl" : "https://app-r.referens.sys.kth.se/my-app/_monitor",
            "applicationUrl" : "https://app-r.referens.sys.kth.se/my-app",
            "friendlyName": "kth-azure-app",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "low"
        }

    }""",
    r"""
        {
        "applicationName": "kth-azure-app",
        "cluster": "missing-cluster",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "created": "",
        "applicationPath": "/my-app",
        
        "mock-expected": {
            "monitorUrl" : "https://app.kth.se/my-app/_monitor",
            "applicationUrl" : "https://app.kth.se/my-app",
            "friendlyName": "kth-azure-app",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "low"
        }

    }""",
    r"""
        {
        "applicationName": "kth-azure-app",
        "cluster": "missing-cluster",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "created": "",
        "applicationPath": "/my-app",
        "monitorPath": "http://example.com/url-not-allowed",

        "mock-expected": {
            "monitorUrl" : "https://app.kth.se/my-app/_monitor",
            "applicationUrl" : "https://app.kth.se/my-app",
            "friendlyName": "kth-azure-app",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "low"
        }

    }""",
    r"""
    {
        "applicationName": "kth-azure-app",
        "cluster": "active",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "created": "",
        "applicationPath": "/my-app",
        "monitorUrl": "https://example.com/other-monitoring-url",
        
        "mock-expected": {
            "monitorUrl" : "https://example.com/other-monitoring-url",
            "applicationUrl" : "https://app.kth.se/my-app",
            "friendlyName": "kth-azure-app",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "low"
        }
    }""",

    r"""
    {
        "applicationName": "kth-azure-app",
        "cluster": "active",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "slackChannels": "#team-pipeline,#developers",
        "created": "",
        "importance": "medium",
        "applicationPath": "/kth-azure-app",
        
        "mock-expected": {
            "monitorUrl" : "https://app.kth.se/kth-azure-app/_monitor",
            "applicationUrl" : "https://app.kth.se/kth-azure-app",
            "friendlyName": "kth-azure-app",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "medium"
        }
    }""",
    r"""
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
        "created": "",
        "importance": "high",
        "applicationPath": "/app/my-app/",
        "testAccessibility": "true",
        
        "mock-expected": {
            "monitorUrl" : "https://app.kth.se/app/my-app/_monitor",
            "applicationUrl" : "https://app.kth.se/app/my-app/",
            "friendlyName": "Monitor application",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "high"
        }
    }""",
    r"""
    {
        "applicationName": "kth-azure-app",
        "cluster": "active",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "slackChannels": "#team-pipeline,#developers",
        "publicNameSwedish": "Monitorapp",
        "descriptionSwedish": "Monitorapp för klustret",
        "descriptionEnglish": "Monitor application for cluster",
        "created": "",
        "importance": "high",
        "applicationPath": "/app/my-app/",
        "testAccessibility": "true",
        
        "mock-expected": {
            "monitorUrl" : "https://app.kth.se/app/my-app/_monitor",
            "applicationUrl" : "https://app.kth.se/app/my-app/",
            "friendlyName": "Monitorapp",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "high"
        }
    }""",
    r"""
    {
        "applicationName": "kth-azure-app",
        "cluster": "active",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "slackChannels": "#team-pipeline,#developers",
        "created": "",
        "importance": "high",
        "applicationPath": "/api/my-app/",
        
        "mock-expected": {
            "monitorUrl" : "https://api.kth.se/api/my-app/_monitor",
            "applicationUrl" : "https://api.kth.se/api/my-app/",
            "friendlyName": "kth-azure-app",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "high"
        }
    }""",
    r"""
    {
        "applicationName": "kth-azure-app",
        "cluster": "active",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "slackChannels": "#team-pipeline,#developers",
        "created": "",
        "importance": "high",
        "applicationPath": "/api/my-app/",
        "monitorPattern": "a-string-in-html",
        
        "mock-expected": {
            "monitorUrl" : "https://api.kth.se/api/my-app/_monitor",
            "applicationUrl" : "https://api.kth.se/api/my-app/",
            "friendlyName": "kth-azure-app",
            "monitorPattern": "a-string-in-html",
            "importance": "high"
        }
    }""",
    r"""
    {
        "applicationName": "kth-azure-app",
        "cluster": "active",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "slackChannels": "#team-pipeline,#developers",
        "created": "",
        "importance": "medium",
        "applicationPath": "/api/my-app/",
        "monitorPattern": "a-string-in-html",
        
        "mock-expected": {
            "monitorUrl" : "https://api.kth.se/api/my-app/_monitor",
            "applicationUrl" : "https://api.kth.se/api/my-app/",
            "friendlyName": "kth-azure-app",
            "monitorPattern": "a-string-in-html",
            "importance": "medium"
        }
    }""",
    r"""
    {
        "applicationName": "old-app",
        "cluster": "active",
        "version": "2.0.11_abc123",
        "imageName": "kth-azure-app",
        "slackChannels": "#team-pipeline,#developers",
        "created": "",
        "importance": "medium",
        "applicationPath": "/api/my-app/",
        "monitorPattern": "a-string-in-html",
        "monitorPath": "/apddddi/my-app/_monitor",
        
        "mock-expected": {
            "monitorUrl" : "https://api.kth.se/api/my-app/_monitor",
            "applicationUrl" : "https://api.kth.se/api/my-app/",
            "friendlyName": "old-app",
            "monitorPattern": "a-string-in-html",
            "importance": "medium"
        }
    }""",
    r"""
        {
        "applicationName": "integral-app",
        "cluster": "integral-stage",
        "version": "2.0.11_abc123",
        "imageName": "integral-app",
        "created": "",
        "applicationPath": "/integral-app",
        
        "mock-expected": {
            "monitorUrl" : "https://integral-r.referens.sys.kth.se/integral-app/_monitor",
            "applicationUrl" : "https://integral-r.referens.sys.kth.se/integral-app",
            "friendlyName": "integral-app",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "low"
        }

    }""",
    r"""
        {
        "applicationName": "integral-app",
        "cluster": "integral",
        "version": "2.0.11_abc123",
        "imageName": "integral-app",
        "created": "",
        "applicationPath": "/integral-app",
        
        "mock-expected": {
            "monitorUrl" : "https://integral.sys.kth.se/integral-app/_monitor",
            "applicationUrl" : "https://integral.sys.kth.se/integral-app",
            "friendlyName": "integral-app",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "low"
        }

    }""",
    r"""
        {
        "applicationName": "integral-app",
        "cluster": "integral",
        "version": "2.0.11_abc123",
        "imageName": "integral-app",
        "created": "",
        
        "mock-expected": {
            "monitorUrl" : "",
            "applicationUrl" : "",
            "friendlyName": "integral-app",
            "monitorPattern": "APPLICATION_STATUS: OK",
            "importance": "low"
        }

    }"""
]

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
        "detectifyProfileTokens": "abc123xyz456,987mnb654vcx",
        "testAccessibility": "true"
    }"""

ERROR_STRING = r"""
    {
        "message": "An error occured",
        "slackChannels": "#team-pipeline-logs,#ita-ops",
        "stackTrace": "This is a multiline\nstack trace"
    }
"""

def get_deployment_samples():
    global DEPLOYMENT_SAMPLES_WITH_EXPECTED_VALUES # pylint: disable=W0603
    result = []

    for sample in DEPLOYMENT_SAMPLES_WITH_EXPECTED_VALUES:
        result.append(json.loads(sample))

    return result

def get_raw_deployment():
    global DEPLOYMENT_STRING # pylint: disable=W0603
    return json.loads(DEPLOYMENT_STRING)

def get_deployment_with_defaults():
    global DEPLOYMENT_STRING # pylint: disable=W0603
    return deployment_enricher.enrich(json.loads(DEPLOYMENT_STRING))

def reset_deployment_enricher(deployment):
    if 'monitorUrl' in deployment:
        del deployment['monitorUrl']
    if 'applicationUrl' in deployment:
        del deployment['applicationUrl']
    return deployment_enricher.enrich(deployment)


def get_error():
    global ERROR_STRING # pylint: disable=W0603
    return json.loads(ERROR_STRING)

def expected_value(sample, attribute):
    try: 
        if "mock-expected" in sample:
            return sample["mock-expected"][attribute]
    except Exception as e:
        print(e)
        return None

    return None
