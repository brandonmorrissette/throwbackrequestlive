from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from constructs import Construct
import boto3

class CognitoConstruct(Construct):
    def __init__(self, scope: Construct, id: str, rds, project_name, env, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cognito_client = boto3.client('cognito-idp')
        user_pool = self._user_pool(cognito_client, project_name)
        self.user_pool_id = user_pool.user_pool_id

        self._app_client(cognito_client, self.user_pool_id, project_name)

        groups = self._groups(cognito_client, self.user_pool_id, ["admin", "superuser"])
        self._attach_policies_to_groups(groups, [self._admin_policy(rds)])

    def _user_pool(self, client, project_name):
        existing_pool = self._get_user_pool_by_name(client, project_name + "-user-pool")
        if existing_pool:
            return cognito.UserPool.from_user_pool_id(self, "ExistingUserPool", existing_pool['Id'])
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

    def _app_client(self, client, user_pool_id, project_name):
        existing_client = self._get_app_client_by_name(client, user_pool_id, project_name + "-user-pool-app-client")
        if existing_client:
            return cognito.CfnUserPoolClient.from_user_pool_client_id(self, "ExistingAppClient", existing_client['ClientId'])
        return cognito.CfnUserPoolClient(
            self, "UserPoolAppClient",
            user_pool_id=user_pool_id,
            client_name=f"{project_name}-user-pool-app-client",
            explicit_auth_flows=[
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH"
            ]
        )

    def _groups(self, client, user_pool_id, group_names):
        groups = []
        for group_name in group_names:
            existing_group = self._get_group_by_name(client, user_pool_id, group_name)
            if existing_group:
                groups.append(cognito.CfnUserPoolGroup.from_group_name(self, f"Existing{group_name.capitalize()}Group", group_name))
            else:
                group = cognito.CfnUserPoolGroup(
                    self, f"{group_name}-group",
                    group_name=group_name,
                    user_pool_id=user_pool_id
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

    def _get_user_pool_by_name(self, client, user_pool_name):
        user_pools = client.list_user_pools(MaxResults=60)
        for pool in user_pools.get('UserPools', []):
            if pool['Name'] == user_pool_name:
                return pool
        return None

    def _get_app_client_by_name(self, client, user_pool_id, app_client_name):
        app_clients = client.list_user_pool_clients(UserPoolId=user_pool_id, MaxResults=60)
        for client in app_clients.get('UserPoolClients', []):
            if client['ClientName'] == app_client_name:
                return client
        return None

    def _get_group_by_name(self, client, user_pool_id, group_name):
        groups = client.list_groups(UserPoolId=user_pool_id)
        for group in groups.get('Groups', []):
            if group['GroupName'] == group_name:
                return group
        return None
