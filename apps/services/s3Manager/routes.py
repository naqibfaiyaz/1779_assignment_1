from flask import render_template, redirect, url_for, request
from apps.services.memcache import blueprint
from apps import AWS_ACCESS_KEY, AWS_SECRET_KEY
import boto3

@blueprint.route('/',methods=['GET'])
# Display an HTML list of all s3 buckets.
def s3_list():
    # Let's use Amazon S3
    s3 = boto3.resource('s3')
    # Print out bucket names
    buckets = s3.buckets.all()

    for b in buckets:
        name = b.name

    buckets = s3.buckets.all()

    return render_template("s3_examples/list.html",title="s3 Instances",buckets=buckets)


@blueprint.route('/<id>',methods=['GET'])
#Display details about a specific bucket.
def s3_view(id):
    s3 = boto3.resource('s3')

    bucket = s3.Bucket(id)

    for key in bucket.objects.all():
        k = key

    keys =  bucket.objects.all()


    return render_template("s3_examples/view.html",title="S3 Bucket Contents",id=id,keys=keys)


# @blueprint.route('/upload/<id>',methods=['POST'])
#Upload a new file to an existing bucket
def s3_upload(bucket, file, filename):
    s3 = boto3.client('s3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY)

    s3.upload_fileobj(file, bucket, filename)

    return filename


def s3_getImage(bucketName, key):
    s3 = boto3.client('s3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY)
    
    s3.get_object(
    Bucket=bucketName,
    Key=key)
