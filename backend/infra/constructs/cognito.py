from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import Token
from constructs import Construct
import boto3

class CognitoConstruct(Construct):
    def __init__(self, scope: Construct, id: str, rds, project_name, env, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._cognito_client = boto3.client('cognito-idp')
        self.user_pool = self._user_pool(project_name)

        app_client = self._app_client(project_name)
        admin_group = self._admin_group(rds)
        superuser_group = self._superuser_group(rds)

    def _user_pool(self, project_name):
        user_pool = self._get_user_pool_by_name(project_name + "-user-pool")
        if user_pool:
            return user_pool
        
        return cognito.UserPool(
            self, f"{project_name}-user-pool",
            user_pool_name=f"{project_name}-user-pool",
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

    def _app_client(self, project_name):
        if not Token.is_unresolved(self.user_pool.user_pool_id):
            client = self._get_app_client_by_name(project_name + "-user-pool-app-client")
            if client:
                return client
        
        return cognito.CfnUserPoolClient(
            self, f"{project_name}-user-pool-app-client",
            user_pool_id=self.user_pool.user_pool_id,
            client_name=f"{project_name}-user-pool-app-client",
            explicit_auth_flows=[
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH"
            ]
        )

    def _admin_group(self, rds):
        if not Token.is_unresolved(self.user_pool.user_pool_id):
            group = self._get_group_by_name("admin")
            if group:
                return group
        
        group = cognito.CfnUserPoolGroup(
            self, f"admin",
            group_name="admin",
            user_pool_id=self.user_pool.user_pool_id
        )
        policy = iam.Policy(
            self, "admin-policy",
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
        role = iam.Role(
                    self, f"admin-role",
                    assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
                    inline_policies={f"admin-policy": policy.document}
                )
        group.role_arn = role.role_arn

        return group
    
    def _superuser_group(self, rds):
        if not Token.is_unresolved(self.user_pool.user_pool_id):
            group = self._get_group_by_name("superuser")
            if group:
                return group
        
        group = cognito.CfnUserPoolGroup(
            self, f"superuser",
            group_name="superuser",
            user_pool_id=self.user_pool.user_pool_id
        )
        policy = iam.Policy(
            self, "superuser-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "rds-db:connect",
                        "rds-db:executeStatement",
                        "rds-db:batchExecuteStatement"
                    ],
                    resources=[rds.instance_arn]
                ),
                iam.PolicyStatement(
                    actions=[
                        "cognito-idp:AdminCreateUser",
                        "cognito-idp:AdminDeleteUser",
                        "cognito-idp:AdminUpdateUserAttributes",
                        "cognito-idp:AdminAddUserToGroup",
                        "cognito-idp:AdminRemoveUserFromGroup",
                        "cognito-idp:AdminCreateGroup",
                        "cognito-idp:AdminDeleteGroup",
                        "cognito-idp:AdminUpdateGroup"
                    ],
                    resources=[f"arn:aws:cognito-idp:*:*:userpool/{self.user_pool.user_pool_id}"]
                )
            ]
        )
        role = iam.Role(
                    self, f"superuser-role",
                    assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
                    inline_policies={f"superuser-policy": policy.document}
                )
        group.role_arn = role.role_arn

        return group

    def _get_app_client_by_name(self, app_client_name):
        app_clients = self._cognito_client.list_user_pool_clients(UserPoolId=self.user_pool.user_pool_id, MaxResults=60)
        for client in app_clients.get('UserPoolClients', []):
            if client['ClientName'] == app_client_name:
                return cognito.UserPoolClient.from_user_pool_client_id(
                    self,
                    app_client_name,
                    user_pool_client_id=client["ClientId"]
                )
            
        return None

    def _get_user_pool_by_name(self, user_pool_name):
        user_pools = self._cognito_client.list_user_pools(MaxResults=60)
        for pool in user_pools.get('UserPools', []):
            if pool['Name'] == user_pool_name:
                return cognito.UserPool.from_user_pool_id(
                    self,
                    user_pool_name,
                    user_pool_id=pool["Id"]
                )

        return None

    def _get_group_by_name(self, group_name):
        groups = self._cognito_client.list_groups(UserPoolId=self.user_pool.user_pool_id)
        for group in groups.get('Groups', []):
            if group['GroupName'] == group_name:
                return group

        return None


