from flask import render_template, redirect, url_for, request
from apps.services.cloudWatch import blueprint
from apps import AWS_ACCESS_KEY, AWS_SECRET_KEY
import boto3, datetime
# from ec2_metadata import ec2_metadata

@blueprint.route('/',methods=['GET'])
# Display an HTML list of all s3 buckets.
def put_metric_data_cw(namespaceData, data):
    print(data, AWS_ACCESS_KEY, AWS_SECRET_KEY)
    # Let's use Amazon S3
    try:
        cloudWatch = boto3.client('cloudwatch',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY)
        
        for metric in data:
            metrics=[
                {
                    'MetricName': metric['metricName'],
                    'Dimensions': [
                        {
                            'Name': 'instanceId',
                            'Value': '1'
                        },{
                            'Name': metric['metricName'],
                            'Value': str(metric['value'])
                        },
                    ],
                    'Timestamp': datetime.datetime.now(),
                    'Value': metric['value'],
                    'Unit': metric['unit']
                },
            ]
            
            print(metrics)
            # Print out bucket names
            response = cloudWatch.put_metric_data(
                Namespace=namespaceData,
                MetricData=metrics
            )
    except Exception as e:
        print("Error from test_getMemcacheSize: " + str(e))
        return {
            "success": "false",
            "error": { 
                "code": 500,
                "message": str(e)
                }
            }

    print(response)
    return response