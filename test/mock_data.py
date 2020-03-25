__author__ = 'tinglev@kth.se'

import json
import os
from modules import deployment_enricher

def get_file_as_json(file_path):
    file_path = os.path.join(os.path.dirname(__file__), file_path)
    return json.load(open(file_path))

def get_deployment_samples():
    return get_file_as_json('samples/deployments.json')

def get_deployment_samples_enriched():
    result = []
    for sample in get_deployment_samples():
        sample = deployment_enricher.enrich(sample)
        result.append(sample)
    return result

def get_deployment_sample():
    return get_file_as_json('samples/deployment.json')

def get_deployment_sample_enriched():
    return deployment_enricher.enrich(get_deployment_sample())

def reset_deployment_enricher(deployment):
    if 'monitorUrl' in deployment:
        del deployment['monitorUrl']
    if 'applicationUrl' in deployment:
        del deployment['applicationUrl']
    return deployment_enricher.enrich(deployment)

def get_error():
    return get_file_as_json('samples/error.json')

def get_recommendation_samples():
    return get_file_as_json('samples/recommendations.json')

def expected_value(sample, attribute):
    try:
        if "expected-enriched-values" in sample:
            return sample["expected-enriched-values"][attribute]
    except KeyError as key_err:
        print(key_err)
        return key_err
    return None
