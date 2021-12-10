import requests
import base64
import json
import TestFrameworkCreateBugs

def uploadFiles(org, project, headers, run_id, test_case, index):
    try:
        # Upload Video MP4
        mp4_fn = str(index) + ".mp4"
        mp4_filepath = "./$(bucketDir1)/x1q-29-en_US-portrait/test_cases/" + mp4_fn
        print("Attempting to upload mp4 video: " + mp4_filepath)
        with open(mp4_filepath, "rb") as video_file:
            encoded_string = base64.b64encode(video_file.read())
        uploadFile(org,
                   project,
                   headers,
                   run_id,
                   test_case,
                   index,
                   mp4_fn,
                   encoded_string,
                   "Test Video Attachment Upload")
    except Exception as ex:
        print(ex)
        print("Video Upload Failed for: " + test_case['testCase']['name'])

    try:
        # Upload logcat text
        logcat_fn = str(index) + "_logcat"
        logcat_filepath = "./$(bucketDir1)/x1q-29-en_US-portrait/test_cases/" + logcat_fn
        print("Attempting to upload logcat file: " + logcat_filepath)
        with open(logcat_filepath, "rb") as text_file:
            encoded_string = base64.b64encode(text_file.read())
        uploadFile(org,
                   project,
                   headers,
                   run_id,
                   test_case,
                   index,
                   logcat_fn,
                   encoded_string,
                   "Test Logcat Attachment Upload")
    except Exception as e:
        print(e)
        print("Logcat Upload Failed for: " + test_case['testCase']['name'])

def uploadFile(org, project, headers, run_id, test_case, index, filename, base64_encoded_string, comment):
    data = {
        "fileName": str(filename),
        "comment": str(comment),
        "attachmentType": "GeneralAttachment",
        "stream": base64_encoded_string.decode('UTF-8')
    }
    data_json = json.dumps(data, indent=2)
    test_case_id = test_case['id']
    request_url = "https://dev.azure.com/" + org + "/" + project + "/_apis/test/Runs/"+ str(run_id) + "/Results/" + str(test_case_id) + "/attachments?api-version=6.0-preview.1"

    response = requests.post(
        url=request_url,
        headers=headers,
        data=data_json)
    print("Response Status Result: " + str(response.status_code) + " " + response.text)
    if (response.status_code == 200):
        print("Uploaded " + filename + " for test case: " + test_case['testCase']['name'])
    else:
        print("Failed to upload - " + filename + " for test case: " + test_case['testCase']['name'])

org = "org"
team = "team"

print("Initializing Auth Headers")
headers = TestFrameworkCreateBugs.initializeAuthHeaders()
print("Getting Last Test Run Id")
last_run_id = TestFrameworkCreateBugs.getLastRunId(org, team, headers)
print("")
print("Last Run Id : " + str(last_run_id))
print("Getting Test Cases for: " + str(last_run_id))
all_test_cases = TestFrameworkCreateBugs.getTestCasesByRunId(org, team, last_run_id, headers)
print("")

curr_index = 0
if (all_test_cases):
    for test_case in all_test_cases['value']:
        if TestFrameworkCreateBugs.testFailed(test_case):
            uploadFiles(org, team, headers, last_run_id, test_case, str(curr_index).zfill(4))
        curr_index += 1
