import boto3, os, argparse

class S3_Manager():
    def __init__(self):
        self.s3 = boto3.client("s3", 
            region_name=os.environ['region'], 
            aws_access_key_id=os.environ['access_key'], 
            aws_secret_access_key=os.environ['secret_key'])
    
    def upload_to_bucket(self, filename, dirname, bucketname = 'imt547'):
        '''
        grab file within current directory and place in s3 under same name

        Params : 
        ----------
        filename : string
            filepath of file
        dirname: directory name within s3
        bucketname: name of bucket in s3 - default is imt547 (should be all you need)
        '''
        self.s3.upload_file(Filename = filename, Bucket = bucketname, Key = f'{dirname}/{os.path.basename(filename)}')
        print("Done!")

    def retrieve_from_bucket(self, filename = None, dirname = None, bucketname = 'imt547'):

        if filename and not dirname:
            raise Exception('Provide directory with file')

        resource = boto3.resource("s3", 
            region_name=os.environ['region'], 
            aws_access_key_id=os.environ['access_key'], 
            aws_secret_access_key=os.environ['secret_key'])
        bucket = resource.Bucket(bucketname)
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucketname, Prefix='')

        for page in pages:
            for file in page['Contents']:
                print(file)
                if filename:
                    for obj in self.s3.list_objects(Bucket = bucketname)['Contents']:
                        if os.path.basename(obj['Key']) == filename & os.path.dirname(obj['Key'] == dirname):
                            bucket.download_file(obj['Key'], filename)
                elif dirname:
                    for obj in self.s3.list_objects(Bucket = bucketname)['Contents']:
                        if os.path.dirname(obj['Key']) == dirname:
                            bucket.download_file(obj['Key'], os.path.basename(obj['Key']))
                else:
                    for obj in self.s3.list_objects(Bucket = bucketname)['Contents']:
                        bucket.download_file(obj['Key'], os.path.basename(obj['Key']))
        print("Done!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Interact with aws s3")
    parser.add_argument('-p', '--program', type=str, help='Upload or Retrieve with regards to s3')
    parser.add_argument('-f', '--file', type=str, help='file uploaded into s3')
    args = parser.parse_args()

    program = args.program.upper()
    if program not in ['UPLOAD', 'RETRIEVE']:
        raise Exception('Only Upload or Retrieve values allowed for the arg')

    if args.file and program != 'UPLOAD':
        raise Exception('File arg is useless if you are not uploading')

    s3 = S3_Manager()
    
    if program == 'UPLOAD':
        s3.upload_to_bucket(filename = args.file, dirname='Testing')
    else:
        s3.retrieve_from_bucket()