from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ssm as ssm
from aws_cdk import Token
from constructs import Construct
import logging

class UserPoolConstruct(Construct):
    def __init__(self, scope: Construct, id: str, userpool_name, cognito_client, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self._cognito_client = cognito_client

        self.user_pool = self._user_pool(userpool_name)
        self.app_client = self._app_client(userpool_name)

    def _user_pool(self, userpool_name):
        user_pool = self._get_user_pool_by_name(userpool_name)
        if not user_pool:
            user_pool = cognito.UserPool(
                self, userpool_name,
                user_pool_name=userpool_name,
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

        ssm.StringParameter(
            self,
            f"userpool_name_id",
            string_value=user_pool.user_pool_id,
            parameter_name=f"/{userpool_name}", 
            description="The user pool ID for the Cognito pool",
            tier=ssm.ParameterTier.STANDARD, 
        )
        return user_pool
    
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
    
    def _app_client(self, project_name):
        if not Token.is_unresolved(self.user_pool.user_pool_id):
            logging.info(f"User pool ID: {self.user_pool.user_pool_id}")
            client = self._get_app_client_by_name(project_name + "-user-pool-app-client")
            logging.info(f"Client: {client}")
            if client:
                return client
        
        logging.info(f"Creating app client for {project_name}")
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