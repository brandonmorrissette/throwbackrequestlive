from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from constructs import Construct
import boto3

class CognitoConstruct(Construct):
    def __init__(self, scope: Construct, id: str, rds, project_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        env = kwargs.get('env')

        cognito_client = boto3.client('cognito-idp')

        self.user_pool = self._get_user_pool_by_name(cognito_client, f"{project_name}-UserPool")
        if self.user_pool:
            self.groups = self._get_groups_by_user_pool_id(cognito_client, self.user_pool['Id'])
        else:
            self.user_pool = cognito.UserPool(
                self, f"{project_name}-UserPool",
                user_pool_name=f"{project_name}-UserPool",
                self_sign_up_enabled=False,
                sign_in_aliases=cognito.SignInAliases(email=True),
                password_policy=cognito.PasswordPolicy(
                    min_length=12,
                    require_lowercase=True,
                    require_uppercase=True,
                    require_digits=True,
                    require_symbols=True
                ),
                account_recovery=cognito.AccountRecovery.EMAIL_ONLY
            )

            self.app_client = self.user_pool.add_client(
                "UserPoolAppClient",
                auth_flows=cognito.AuthFlow(
                    admin_user_password=True,
                    user_password=True
                )
            )

            self.groups = self._create_groups()
            self._attach_policies_to_groups(self.groups, [self._create_admin_policy(rds)])
            
        self.create_superuser_lambda(self.user_pool)

    def _create_groups(self):
        admin_group = cognito.CfnUserPoolGroup(
            self, "AdminGroup",
            group_name="Admin",
            user_pool_id=self.user_pool.user_pool_id
        )

        superuser_group = cognito.CfnUserPoolGroup(
            self, "SuperuserGroup",
            group_name="Superuser",
            user_pool_id=self.user_pool.user_pool_id
        )

        return [admin_group, superuser_group]

    def _create_admin_policy(self, rds):
        return iam.Policy(
            self, "AdminPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "rds-db:connect",
                        "rds-db:executeStatement",
                        "rds-db:batchExecuteStatement"
                    ],
                    resources=[rds.instance_arn]
                )
            ]
        )

    def _attach_policies_to_groups(self, groups, policies):
        for group in groups:
            for policy in policies:
                role = iam.Role(
                    self, f"{group.group_name}Role",
                    assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
                    inline_policies={f"{group.group_name}Policy": policy.document}
                )
                group.role_arn = role.role_arn

    def _get_user_pool_by_name(self, client, user_pool_name):
        user_pools = client.list_user_pools(MaxResults=60)
        for pool in user_pools['UserPools']:
            if pool['Name'] == user_pool_name:
                return pool
        return None

    def _get_groups_by_user_pool_id(self, client, user_pool_id):
        groups = client.list_groups(UserPoolId=user_pool_id)
        return groups['Groups']

    def create_superuser_lambda(self, user_pool):
        create_superuser_lambda = _lambda.Function(
            self, 'CreateSuperuserLambda',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='create_superuser.handler',
            code=_lambda.Code.from_asset('infra/setup/lambda/create_superuser'),
            environment={
                'USER_POOL_ID': user_pool.user_pool_id,
                'SUPERUSER_GROUP_NAME': "Superuser"
            },
            function_name='create-superuser-lambda'
        )

        create_superuser_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "cognito-idp:AdminGetUser",
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminAddUserToGroup"
                ],
                resources=[f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{user_pool.user_pool_id}"]
            )
        )