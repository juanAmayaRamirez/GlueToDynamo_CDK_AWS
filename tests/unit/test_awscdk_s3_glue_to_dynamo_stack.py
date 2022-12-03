import aws_cdk as core
import aws_cdk.assertions as assertions

from awscdk_s3_glue_to_dynamo.awscdk_s3_glue_to_dynamo_stack import AwscdkS3GlueToDynamoStack

# example tests. To run these tests, uncomment this file along with the example
# resource in awscdk_s3_glue_to_dynamo/awscdk_s3_glue_to_dynamo_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwscdkS3GlueToDynamoStack(app, "awscdk-s3-glue-to-dynamo")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
