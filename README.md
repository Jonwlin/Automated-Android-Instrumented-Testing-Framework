Welcome to this Tutorial Demo for Automated Instrumented tests using AppCenter/Firebase

- In python-automation directory, you can find 3 python script files
    - ExtractBucketDir.py: uses a regex to find the Gcloud's Bucket Directory your instrumented test files were saved to
    - ParseResultsCreateBugs.py: parses the results of the most recent Test Run and pulls Gcloud metadata to create bugs
    - UploadTestResultAttachments.py: will attach Gcloud metadata to the actual test results within ADO

## App Center Testing
[App Center Test in Azure DevOps](https://docs.microsoft.com/en-us/appcenter/test-cloud/vsts-plugin)

[App Center CLI Setup Guide](https://docs.microsoft.com/en-us/appcenter/cli/)

[App Center Github CLI Reference](https://github.com/microsoft/appcenter-cli) 

[App Center Test Lab Pricing](https://visualstudio.microsoft.com/app-center/pricing/) 

#### App Center Pricing

 - $99/month for 30-hours on each physical device

## Gcloud Testing

[Gcloud Firebase CLI Setup Guide](https://firebase.google.com/docs/test-lab/android/command-line) 

[Gcloud Firebase CLI Reference](https://cloud.google.com/sdk/gcloud/reference/firebase/test/android/run) 

[Gcloud Firebase Pricing](https://firebase.google.com/docs/test-lab/usage-quotas-pricing#:~:text=%245%20per%20hour%20for%20each,hour%20for%20each%20virtual%20device) 

#### Blaze plan: Minutes spent running tests. The Blaze plan begins with a free time limit that's similar to the resource limit offered by the Spark plan:
- 30 minutes of test time per day on physical devices
- 60 minutes of test time per day on virtual devices
#### Any usage above these limits are charged by the following hourly rates:
- $5 per hour for each physical device
- $1 per hour for each virtual device

## Azure DevOps Pipeline Hosted Emulator Testing

[Test on an Android Emulator](https://docs.microsoft.com/en-us/azure/devops/pipelines/ecosystems/android?view=azure-devops#test-on-the-android-emulator)


## Azure DevOps Pipelines




