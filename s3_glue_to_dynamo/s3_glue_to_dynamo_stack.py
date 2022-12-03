from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_glue as glue,
    # aws_sqs as sqs,
    aws_s3_deployment as s3deploy,
    DefaultStackSynthesizer
    
)
from constructs import Construct

class AwscdkS3GlueToDynamoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, synthesizer: DefaultStackSynthesizer, **kwargs) -> None:
        super().__init__(scope, construct_id,**kwargs)

        # BUCKET ASSETS

        ## create glue bucket for assets/script
        bucket= s3.Bucket(self, 'cdk-gluejobassetsbucket',
            versioned= True,
            bucket_name= "cdk-glue-job-bucket-example-xxxxas"
        )


        # IAM GLUE ROLE
        ## creating role
        glueRole = iam.Role(
            self, 'cdk-my-glue-job-role',
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            description="this is a role for aws-cdk deployed glue",
            role_name="BURoleForCDKGlue"
        )
        
        ## creating glue policies
        ### managed policy
        glueManagedPolicy = iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
        ### inline-policy
        glueBucketReadPolicy=iam.Policy(self,"cdk-glue-policy",
            policy_name='BUPolicyForCDKGlue',
            statements=[iam.PolicyStatement(
                actions=[
                    "s3:GetBucket*",
                    "s3:GetObject*",
                    "s3:List*"],
                resources=[
                    bucket.bucket_arn,
                    bucket.bucket_arn+'/*'],
                effect=iam.Effect.ALLOW
            )]
        )
        ## attaching glue policy to role
        ### managed policy
        glueRole.add_managed_policy(glueManagedPolicy)
        ### inline policy
        glueRole.attach_inline_policy(glueBucketReadPolicy)

        # GLUE JOB
        ## create python glue job
        glue.CfnJob(self, 'cdk-glue-job',
            role=glueRole.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name='pythonshell',
                python_version='3',
                script_location='s3://cdk-glue-job-bucket-example-xxxxas/glue-python-scripts/gluescript.py'
            )
        )
        
        # UPLOAD GLUE ASSETS
        ## IAM Assets Role
        assetsRole = iam.Role(
            self, 'cdk-assets-glue-job-role',
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="this is a role for aws-cdk assets upload for glue",
            role_name="BURoleForScriptUpload"
        )
        
        ## IAM Assets Policies 
        ### managed assets policy
        assetsManagedPolicy = iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        ### inline assets policy
        assetsBucketReadPolicy=iam.Policy(self,"cdk-assets-policy",
            policy_name='BUPolicyForCDKAssetsGlue',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "s3:GetBucket*",
                        "s3:GetObject*",
                        "s3:List*"],
                    resources=[
                        "arn:aws:s3:::"+synthesizer.DEFAULT_FILE_ASSETS_BUCKET_NAME,
                        "arn:aws:s3:::"+synthesizer.DEFAULT_FILE_ASSETS_BUCKET_NAME+'/*'],
                    effect=iam.Effect.ALLOW
                ),
                iam.PolicyStatement(
                    actions=[
                        "s3:Abort*",
                        "s3:DeleteObject*",
                        "s3:GetBucket*",
                        "s3:GetObject*",
                        "s3:List*",
                        "s3:PutObject",
                        "s3:PutObjectLegalHold",
                        "s3:PutObjectRetention",
                        "s3:PutObjectTagging",
                        "s3:PutObjectVersionTagging"],
                    resources=[
                        bucket.bucket_arn,
                        bucket.bucket_arn+'/*'],
                    effect=iam.Effect.ALLOW
                )
            ]
        )
        ## attaching glue policy to role
        ### managed policy
        assetsRole.add_managed_policy(assetsManagedPolicy)
        ### inline policy
        assetsRole.attach_inline_policy(assetsBucketReadPolicy)
        ## uploading assets to bucket
        s3deploy.BucketDeployment(self, 'DeployGlueJobFiles',
            sources=[s3deploy.Source.asset('./assets/glue-scripts')],
            destination_bucket=bucket,
            destination_key_prefix='glue-python-scripts',
            role=assetsRole
        )