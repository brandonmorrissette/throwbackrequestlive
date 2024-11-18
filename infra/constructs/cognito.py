from aws_cdk import aws_cognito as cognito
from constructs import Construct


class CognitoConstruct(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.user_pool = cognito.UserPool(
            self, "UserPool",
            self_sign_up_enabled=False,
            user_pool_name="UserPool",
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

        self.admin_group = cognito.CfnUserPoolGroup(
            self, "AdminGroup",
            group_name="Admin",
            user_pool_id=self.user_pool.user_pool_id
        )
