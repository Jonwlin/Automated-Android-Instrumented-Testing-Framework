import requests
import base64
import json
import sys
import re

# Token Scope:
#  - Work Item - Read, Write (vso.work_write)
#  - Test Runs - Read, Write, Manage (vso.test)
ado_token = sys.argv[1]
assigned_to = sys.argv[2]
commit_id = sys.argv[3]
build_uri = sys.argv[4]

# Initialize Header Authorization
def initializeAuthHeaders(token, content_type):
    authorization = str(base64.b64encode(bytes(':'+ token, 'ascii')), 'ascii')
    auth_headers = {
        "Content-Type": content_type,
        'Accept': 'application/json',
        'Authorization': 'Basic '+ authorization
    }
    return auth_headers

# GET: the most recent run id
def getLastRunId(token, org, project):
    headers = initializeAuthHeaders(token, "application/json")

    request_url = base_ado_url + org + "/" + project + "/_apis/test/runs?api-version=6.0"
    response = requests.get(url=request_url, headers=headers)

    if (response.status_code == 200):
        all_test_runs = json.loads(response.text)
        if (isFirebaseTestRun(all_test_runs['value'][-1]['name'])):
            return all_test_runs['value'][-1]['id']
        else:
            raise ValueError("Last Run's ID was not a Firebase Test Result - Unable to Process")
    else:
        raise ConnectionError("Failed getLastRunId: " + str(response.status_code))

# Must match JUnit_TestResults_6011 to be Firebase Test
def isFirebaseTestRun(testname):
    matched = re.match("JUnit_TestResults_\d{4}", testname)
    return bool(matched)

# GET: the most recent run's Build URL
def getTestResultsUrl(token, org, project):
    headers = initializeAuthHeaders(token, "application/json")

    request_url = base_ado_url + org + "/" + project + "/_apis/test/runs?api-version=6.0"
    response = requests.get(url=request_url, headers=headers)

    if (response.status_code == 200):
        all_test_runs = json.loads(response.text)
        return all_test_runs['value'][-1]['webAccessUrl']
    else:
        raise ConnectionError("Failed getTestResultsUrl: " + str(response.status_code))

# Get all test cases for a run by id
def getTestCasesByRunId(token, org, project, run_id):
    headers = initializeAuthHeaders(token, 'application/json')

    request_url = base_ado_url + org + "/" + project + "/_apis/test/Runs/" + str(run_id) + "/results?api-version=6.0"
    response = requests.get(headers=headers, url=request_url)

    if (response.status_code == 200):
        print("Successfully retrieved test cases by run id: " + str(run_id) + "\n")
        return json.loads(response.text)
    else:
        raise ConnectionError("Failed getTestCasesByRunId: " + str(response.status_code))

# GET: Current Iteration Path
def getCurrentIterationPath(token, org, team, project):
    headers = initializeAuthHeaders(token, "application/json-patch+json")

    request_url = base_ado_url + org + "/" + team + "/" + project + "/_apis/work/teamsettings/iterations?api-version=6.0"
    response = requests.get(headers=headers, url=request_url)

    if (response.status_code == 200):
        values = json.loads(response.text)['value']
        for value in values:
            if (value['attributes']['timeFrame'] == "current"):
                current_iteration_path = value['path']
                print("Current Iteration Path: " + value['path'])
        return current_iteration_path
    else:
        raise ConnectionError("Failed getCurrentIterationPath: " + str(response.status_code))

# POST: Upload file to ADO Attachments, Response URL saved for Attaching to WI
def uploadFileAttachment(token, org, team, filename, filepath):
    headers = initializeAuthHeaders(token, 'application/octet-stream')

    with open(filepath, 'rb') as f:
        data = f.read()

    request_url = base_ado_url + org + "/" + team + "/_apis/wit/attachments?fileName=" + filename + "&api-version=6.0"
    response = requests.post(headers=headers, url=request_url, data=data)

    if (response.status_code == 201):
        print("Successfully Uploaded: " + filename)
        return json.loads(response.text)['url']
    else:
        raise ConnectionError("Failed to upload - " + filename + " - Response Status Code: " + str(response.status_code))

# Create an array for Video and Logcat Attachments for a Work item
def createAttachmentJsons(video_url, logcat_url, test_results_url, commit_id, build_uri):
    attachment_jsons = [
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "AttachedFile",
                "url": video_url,
                "attributes": {
                    "comment": "Test App Video Recording for Test Case"
                }
            }
        },
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "AttachedFile",
                "url": logcat_url,
                "attributes": {
                    "comment": "Logcat for Test Case"
                }
            }
        },
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "Hyperlink",
                "url": test_results_url
            }
        },
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "ArtifactLink",
                "url": "vstfs:///Git/Commit/ffca2707-8989-4012-8fa4-5998fa8d078a%2Fd95544fb-1442-480b-a5dc-d5f313212108%2F" + commit_id,
                "attributes": {
                    "name": "Fixed in Commit"
                }
            }
        },
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "ArtifactLink",
                "url": build_uri,
                "attributes": {
                    "name": "Build"
                }
            }
        }
    ]
    return attachment_jsons

# POST: Query Work items with test case name to check if already exists
def doesWorkItemAlreadyExist(token, org, team, project, test_case_name):
    headers = initializeAuthHeaders(token, "application/json")

    request_url = base_ado_url + org + "/" + team + "/" + project + "/_apis/wit/wiql?api-version=6.1-preview.2"
    data = {
        "query": "Select [System.Id], [System.Title], [System.State] From WorkItems Where [System.Title] CONTAINS '" + test_case_name + "' AND [State] <> 'Closed' AND [State] <> 'Removed'"
    }
    data_json = json.dumps(data, indent=2)
    response = requests.post(headers=headers, url=request_url, data=data_json)

    if (response.status_code == 200):
        response_json = json.loads(response.text)
        return len(response_json['workItems']) > 0
    else:
        raise ConnectionError("Failed doesWorkItemAlreadyExist: " + str(response.status_code))

# Checks if Test Out Passed
def testFailed(test_case):
    return (test_case['outcome'] != "Passed")

# POST: Create Work Item in Azure Devops
def createWorkItem(token, org, team, wi_type, title, assigned_to, iteration_path, repro_steps="", system_info="", attachment_jsons=[]):
    headers = initializeAuthHeaders(token, "application/json-patch+json")

    request_url = base_ado_url + org + "/" + team + "/_apis/wit/workitems/$" + wi_type + "?api-version=6.0&bypassRules=true"
    domainName = title.split(": ")[-1][:-1]
    data = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "from": "null",
            "value": title
        },
        {
            "op": "add",
            "path": "/fields/System.State",
            "from": "null",
            "value": "New"
        },
        {
            "op": "add",
            "path": "/fields/System.AssignedTo",
            "value": assigned_to
        },
        {
            "op": "add",
            "path": "/fields/System.IterationPath",
            "value": iteration_path
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.TCM.SystemInfo",
            "value": system_info
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.TCM.ReproSteps",
            "value": repro_steps
        },
        {
            "op": "add",
            "path": "/fields/System.Tags",
            "value": "1ClickPassword; Untriaged"
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Priority",
            "value": 3
        },
        {
            "op": "add",
            "path": "/fields/Custom.Domain",
            'value': domainName
        }
    ]

    # startChangePassword[Checking domain: 23andme.com]
    # If Video and Logcat URLs are Available for Attachment
    for attachment_json in attachment_jsons:
        data.append(attachment_json)

    data_json = json.dumps(data, indent=2)
    response = requests.post(headers=headers, url=request_url, data=data_json)
    print("Result of Create Bug for: " + title + " - Status Code: " + str(response.status_code))
    return response

## Start Parsing, Uploading attachments, Creating Bugs for Firebase Test Failures
## Static Variables for Reuse
base_ado_url = "https://dev.azure.com/"
gsutils_output_dir = "./x1q-29-en_US-portrait/test_cases/"
mp4_ext = ".mp4"
logcat_ext = "_logcat"
org = "<org>"
team = "<team>"


print("Starting Parse Test Results, Create Video and Logcat Attachment, and Bugs for each Failed Firebase Test\n")
print("Getting Last Test Run Id")
last_run_id = getLastRunId(ado_token, org, team)
print("Last Run Id : " + str(last_run_id) + "\n")
print("Getting Test Results Url")
test_results_url = getTestResultsUrl(ado_token, org, team)
print(test_results_url + "\n")
print("Getting Test Cases for: " + str(last_run_id))
all_test_cases = getTestCasesByRunId(ado_token, org, team, last_run_id)

print("Retrieving Current Sprint Iteration")
current_iteration = getCurrentIterationPath(ado_token, org, team, "<project name>")

curr_index = 0
bug_count = 0
for test_case in all_test_cases['value']:
    workItemExists = doesWorkItemAlreadyExist(ado_token, org, team, "<project name>", test_case['testCaseTitle'])
    if not testFailed(test_case):
        print("Test Case " + test_case['testCase']['name'] + ": Succeeded")
    elif testFailed(test_case) and workItemExists:
        print("Test Case " + test_case['testCase']['name'] + ": Failed -- Bug Already Exists")
    elif testFailed(test_case) and not workItemExists:
        print("\nCreating a Bug for Failed Test: " + test_case['testCase']['name'])

        file_index = str(curr_index).zfill(4)
        domainName = test_case['testCase']['name'].split(": ")[-1][:-1]
        video_url = uploadFileAttachment(ado_token, org, team, domainName + mp4_ext, gsutils_output_dir + file_index + mp4_ext)
        logcat_url = uploadFileAttachment(ado_token, org, team, domainName + logcat_ext + ".txt", gsutils_output_dir + file_index + logcat_ext)

        bug_count += 1
        response = createWorkItem(ado_token,
                       org,
                       team,
                       "bug",
                       "Firebase Test Failure: " + test_case['testCase']['name'],
                       assigned_to,
                       current_iteration,
                       "Firebase Instrumented Test Case Failure - Logs and Video are Attached",
                       test_case['stackTrace'],
                       createAttachmentJsons(video_url, logcat_url, test_results_url, commit_id, build_uri))

        if (response.status_code == 200):
            print("Successfully created Bug for - " + test_case['testCase']['name'] + "\n")
        else:
            print("Failed to create Bug for - " + test_case['testCase']['name'] + "\n")
    curr_index += 1

print("\nFinished -- Parsing and creating bugs for all test cases")
print("Bugs Created: " + str(bug_count))