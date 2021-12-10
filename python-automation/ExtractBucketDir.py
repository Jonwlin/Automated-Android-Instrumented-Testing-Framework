import re

# Parse file and extract google bucket dir
def extractBucketDir(filepath):
    pattern = re.compile("test-lab-.*-.*\/\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}\..*_.*\/", re.MULTILINE)

    with open(filepath) as f:
        BucketDir = re.search(pattern, f.read()).group(0)

    print("BucketDir = " + BucketDir)
    print("##vso[task.setvariable variable=BucketDir]" + BucketDir)
    return BucketDir
