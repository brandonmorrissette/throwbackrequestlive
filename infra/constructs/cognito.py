from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from constructs import Construct

class CognitoConstruct(Construct):
    def __init__(self, scope: Construct, id: str, superuser_email: str, rds, project_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

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

        self.admin_group = cognito.CfnUserPoolGroup(
            self, "AdminGroup",
            group_name="Admin",
            user_pool_id=self.user_pool.user_pool_id
        )

        self.superuser_group = cognito.CfnUserPoolGroup(
            self, "SuperuserGroup",
            group_name="Superuser",
            user_pool_id=self.user_pool.user_pool_id
        )

        self.attach_policies_to_groups([self.admin_group, self.superuser_group], [self.create_admin_policy(rds)])

    def create_admin_policy(self, rds):
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

    def attach_policies_to_groups(self, groups, policies):
        for group in groups:
            for policy in policies:
                role = iam.Role(
                    self, f"{group.group_name}Role",
                    assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
                    inline_policies={f"{group.group_name}Policy": policy.document}
                )
                group.role_arn = role.role_arn