from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from constructs import Construct
import boto3

class CognitoConstruct(Construct):
    def __init__(self, scope: Construct, id: str, rds, project_name, env, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cognito_client = boto3.client('cognito-idp')

        user_pool = self._get_user_pool_by_name(cognito_client, f"{project_name}-UserPool")
        user_pool_id = user_pool['Id'] if user_pool else None
        if not user_pool:
            user_pool = cognito.UserPool(
                self, f"{project_name}-UserPool",
                user_pool_name=f"{project_name}-UserPool",
                self_sign_up_enabled=False,
                sign_in_aliases=cognito.SignInAliases(email=True),
                password_policy=cognito.PasswordPolicy(
                    min_length=8,
                    require_lowercase=False,
                    require_uppercase=False,
                    require_digits=False,
                    require_symbols=False
                ),
                account_recovery=cognito.AccountRecovery.EMAIL_ONLY
            )
            user_pool_id = user_pool.user_pool_id
            
        app_client = self._get_app_client_by_name(cognito_client, user_pool_id, f"{project_name}-UserPool-AppClient")
        if not app_client:
            app_client = cognito.CfnUserPoolClient(
                self, f"{project_name}-UserPool-AppClient",
                user_pool_id=user_pool_id,
                client_name=f"{project_name}-UserPool-AppClient",
                explicit_auth_flows=[
                    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                    "ALLOW_USER_PASSWORD_AUTH",
                    "ALLOW_REFRESH_TOKEN_AUTH"
                ]
            )

        self._attach_policies_to_groups(self._create_groups(cognito_client, user_pool_id), [self._create_admin_policy(rds)])
        self.create_superuser_lambda(user_pool_id, env)

    def _create_groups(self, client, user_pool_id):
        groups = []

        admin_group = self._get_group_by_name(client, user_pool_id, "Admin")
        if not admin_group:
            admin_group = cognito.CfnUserPoolGroup(
                self, "AdminGroup",
                group_name="Admin",
                user_pool_id=user_pool_id
            )
            groups.append(admin_group)

        superuser_group = self._get_group_by_name(client, user_pool_id, "Superuser")
        if not superuser_group:
            superuser_group = cognito.CfnUserPoolGroup(
                self, "SuperuserGroup",
                group_name="Superuser",
                user_pool_id=user_pool_id
            )
            groups.append(superuser_group)

        return groups

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

    def _get_app_client_by_name(self, client, user_pool_id, app_client_name):
        app_clients = client.list_user_pool_clients(UserPoolId=user_pool_id, MaxResults=60)
        for client in app_clients['UserPoolClients']:
            if client['ClientName'] == app_client_name:
                return client
        return None

    def _get_group_by_name(self, client, user_pool_id, group_name):
        groups = client.list_groups(UserPoolId=user_pool_id)
        for group in groups['Groups']:
            if group['GroupName'] == group_name:
                return group
        return None

    def create_superuser_lambda(self, user_pool_id, env):
        create_superuser_lambda = _lambda.Function(
            self, 'CreateSuperuserLambda',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='create_superuser.handler',
            code=_lambda.Code.from_asset('./infra/setup/lambda/create_superuser'),
            environment={
            'USER_POOL_ID': user_pool_id,
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
                resources=[f"arn:aws:cognito-idp:{env.region}:{env.account}:userpool/{user_pool_id}"]
            )
        )