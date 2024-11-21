from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from constructs import Construct

class CognitoConstruct(Construct):
    def __init__(self, scope: Construct, id: str, superuser_email: str, rds, project_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.user_pool = cognito.UserPool(
            self, f"{project_name}-UserPool",
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

        self.attach_admin_permissions_to_groups(rds)

        self.create_superuser(superuser_email)

    def attach_admin_permissions_to_groups(self, rds):
        admin_policy = iam.Policy(
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

        admin_role = iam.Role(
            self, "AdminRole",
            assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
            inline_policies={"AdminPolicy": admin_policy.document}
        )

        self.admin_group.role_arn = admin_role.role_arn
        self.superuser_group.role_arn = admin_role.role_arn

    def create_superuser(self, superuser_email: str):
        superuser = cognito.CfnUserPoolUser(
            self, "Superuser",
            user_pool_id=self.user_pool.user_pool_id,
            desired_delivery_mediums=["EMAIL"],
            user_attributes=[cognito.CfnUserPoolUser.AttributeTypeProperty(
                name="email",
                value=superuser_email
            )],
        )
