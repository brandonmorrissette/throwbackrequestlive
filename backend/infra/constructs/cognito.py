from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import Token
from constructs import Construct
import boto3

class CognitoConstruct(Construct):
    def __init__(self, scope: Construct, id: str, rds, project_name, env, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cognito_client = boto3.client('cognito-idp')
        self.user_pool = self._user_pool(cognito_client, project_name)

        self._app_client(cognito_client, project_name)

        groups = self._groups(cognito_client, ["admin", "superuser"])
        self._attach_policies_to_groups(groups, [self._admin_policy(rds)])

    def _user_pool(self, client, project_name):
        user_pool = self._get_user_pool_by_name(client, project_name + "-user-pool")
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

    def _app_client(self, client, project_name):
        if not Token.is_unresolved(self.user_pool.user_pool_id):
            client = self._get_app_client_by_name(client, project_name + "-user-pool-app-client")
            if client:
                return client
        
        return cognito.CfnUserPoolClient(
            self, "UserPoolAppClient",
            user_pool_id=self.user_pool.user_pool_id,
            client_name=f"{project_name}-user-pool-app-client",
            explicit_auth_flows=[
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH"
            ]
        )

    def _groups(self, client, group_names):
        groups = []
        for group_name in group_names:
            if not Token.is_unresolved(self.user_pool.user_pool_id):
                group = self._get_group_by_name(client, group_name)
                if group:
                    groups.append(group)
                    continue
            
            group = cognito.CfnUserPoolGroup(
                self, f"{group_name}",
                group_name=group_name,
                user_pool_id=self.user_pool.user_pool_id
            )
            groups.append(group)
        return groups

    def _admin_policy(self, rds):
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

    def _get_app_client_by_name(self, client, app_client_name):
        app_clients = client.list_user_pool_clients(UserPoolId=self.user_pool.user_pool_id, MaxResults=60)
        for client in app_clients.get('UserPoolClients', []):
            if client['ClientName'] == app_client_name:
                return cognito.UserPoolClient.from_user_pool_client_id(
                    self,
                    app_client_name,
                    user_pool_client_id=client["ClientId"]
                )
            
        return None

    def _get_user_pool_by_name(self, client, user_pool_name):
        user_pools = client.list_user_pools(MaxResults=60)
        for pool in user_pools.get('UserPools', []):
            if pool['Name'] == user_pool_name:
                return cognito.UserPool.from_user_pool_id(
                    self,
                    user_pool_name,
                    user_pool_id=pool["Id"]
                )

        return None

    def _get_group_by_name(self, client, group_name):
        groups = client.list_groups(UserPoolId=self.user_pool.user_pool_id)
        for group in groups.get('Groups', []):
            if group['GroupName'] == group_name:
                return cognito.CfnUserPoolGroup(
                    self,
                    f"{group_name}-group",
                    group_name=group["GroupName"],
                    user_pool_id=self.user_pool.user_pool_id
                )

        return None


