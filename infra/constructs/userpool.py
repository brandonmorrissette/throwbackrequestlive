import logging

from aws_cdk import RemovalPolicy, Token
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ssm as ssm
from constructs import Construct

logging.basicConfig(level=logging.INFO)


class UserPoolConstruct(Construct):
    def __init__(
        self, scope: Construct, id: str, userpool_name, cognito_client
    ) -> None:
        super().__init__(scope, id)
        self._cognito_client = cognito_client

        self.user_pool = self._user_pool(userpool_name)
        self._post_user_pool_id(userpool_name, self.user_pool.user_pool_id)
        self.app_client = self._app_client(userpool_name)
        self._post_app_client_id(f"{userpool_name}-app-client", self.app_client.ref)

    def _user_pool(self, userpool_name):
        user_pool = self._get_user_pool_by_name(userpool_name)
        if not user_pool:
            user_pool = cognito.UserPool(
                self,
                f"{userpool_name}-{self.node.addr}",
                user_pool_name=userpool_name,
                self_sign_up_enabled=False,
                sign_in_aliases=cognito.SignInAliases(email=True),
                password_policy=cognito.PasswordPolicy(
                    min_length=8,
                    require_lowercase=False,
                    require_uppercase=False,
                    require_digits=False,
                    require_symbols=False,
                ),
                account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
                removal_policy=RemovalPolicy.DESTROY,
            )

        return user_pool

    def _post_user_pool_id(self, user_pool_name, user_pool_id):
        user_pool_id_param_id = f"{user_pool_name}-{self.node.addr}-id"
        param_name = f"/{user_pool_name}-id"
        self._post_string_param(
            user_pool_id_param_id, param_name, user_pool_id, "Cognito User Pool ID"
        )

    def _post_app_client_id(self, app_client_name, app_client_id):
        app_client_id_param_id = f"{app_client_name}-{self.node.addr}-id"
        param_name = f"/{app_client_name}-id"
        self._post_string_param(
            app_client_id_param_id, param_name, app_client_id, "Cognito App Client ID"
        )

    def _post_string_param(self, param_id, param_name, param_value, description=None):
        if self.node.try_find_child(param_id):
            self.node.try_remove_child(param_id)

        ssm_param = ssm.StringParameter(
            self,
            param_id,
            parameter_name=param_name,
            string_value=param_value,
            description=description,
        )
        ssm_param.apply_removal_policy(RemovalPolicy.DESTROY)

    def _get_user_pool_by_name(self, user_pool_name):
        user_pools = self._cognito_client.list_user_pools(MaxResults=60)
        for pool in user_pools.get("UserPools", []):
            if pool["Name"] == user_pool_name:
                user_pool = cognito.UserPool.from_user_pool_id(
                    self, user_pool_name, user_pool_id=pool["Id"]
                )

        return None

    def _app_client(self, project_name):
        if not Token.is_unresolved(self.user_pool.user_pool_id):
            client = self._get_app_client_by_name(
                project_name + "-user-pool-app-client"
            )
            if client:
                return client

        return cognito.CfnUserPoolClient(
            self,
            f"{project_name}-user-pool-app-client",
            user_pool_id=self.user_pool.user_pool_id,
            client_name=f"{project_name}-user-pool-app-client",
            explicit_auth_flows=[
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
        )

    def _get_app_client_by_name(self, app_client_name):
        app_clients = self._cognito_client.list_user_pool_clients(
            UserPoolId=self.user_pool.user_pool_id, MaxResults=60
        )
        for client in app_clients.get("UserPoolClients", []):
            if client["ClientName"] == app_client_name:
                return cognito.UserPoolClient.from_user_pool_client_id(
                    self, app_client_name, user_pool_client_id=client["ClientId"]
                )

        return None
