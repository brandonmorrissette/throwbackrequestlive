import boto3
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from constructs import Construct
from constructs.userpool import UserPoolConstruct


class UserManagementStack(Stack):

    def __init__(
        self,
        scope: Construct,
        id: str,
        rds,
        project_name: str,
        env,
        execution_role,
        log_group,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self._cognito_client = boto3.client("cognito-idp")
        user_pool_name = f"{project_name}-user-pool"
        self.user_pool_construct = UserPoolConstruct(
            self,
            f"{project_name}-user-pool-construct",
            user_pool_name,
            self._cognito_client,
            **kwargs,
        )

        admin_rds_policy = iam.ManagedPolicy(
            self,
            "admin-rds-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "rds-db:connect",
                        "rds-db:executeStatement",
                        "rds-db:batchExecuteStatement",
                    ],
                    resources=[rds.instance_arn],
                )
            ],
        )

        cognito_policy = iam.ManagedPolicy(
            self,
            "cognito-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "cognito-idp:AdminCreateUser",
                        "cognito-idp:AdminDeleteUser",
                        "cognito-idp:AdminUpdateUserAttributes",
                        "cognito-idp:AdminAddUserToGroup",
                        "cognito-idp:AdminRemoveUserFromGroup",
                        "cognito-idp:AdminCreateGroup",
                        "cognito-idp:AdminDeleteGroup",
                        "cognito-idp:AdminUpdateGroup",
                    ],
                    resources=[
                        f"arn:aws:cognito-idp:{env.region}:{env.account}:userpool/{self.user_pool_construct.user_pool.user_pool_id}"
                    ],
                )
            ],
        )

        admin_group = cognito.CfnUserPoolGroup(
            self,
            "admin-group",
            user_pool_id=self.user_pool_construct.user_pool.user_pool_id,
            group_name="admin",
        )

        admin_role = iam.Role(
            self,
            "admin-role",
            assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
        )

        admin_role.add_managed_policy(admin_rds_policy)

        superuser_group = cognito.CfnUserPoolGroup(
            self,
            "SuperuserGroup",
            user_pool_id=self.user_pool_construct.user_pool.user_pool_id,
            group_name="superuser",
        )

        superuser_role = iam.Role(
            self,
            "superuser-role",
            assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
        )
        superuser_role.add_managed_policy(admin_rds_policy)
        superuser_role.add_managed_policy(cognito_policy)

        superuser_task_role = iam.Role(
            self,
            "SuperuserTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            inline_policies={
                "SuperuserPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "cognito-idp:AdminGetUser",
                                "cognito-idp:AdminCreateUser",
                                "cognito-idp:AdminAddUserToGroup",
                            ],
                            resources=[
                                f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{self.user_pool_construct.user_pool.user_pool_id}"
                            ],
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "cognito-idp:ListUserPools",
                            ],
                            resources=["*"],
                        ),
                    ]
                )
            },
        )

        superuser_task_definition = ecs.FargateTaskDefinition(
            self,
            "superuser-task-definition",
            memory_limit_mib=512,
            cpu=256,
            execution_role=execution_role,
            task_role=superuser_task_role,
        )

        superuser_task_definition.add_container(
            "superuser-container",
            image=ecs.ContainerImage.from_asset(
                "infra/environment_setup/create_superuser"
            ),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="superuser-creation",
                log_group=log_group,
            ),
        )

        CfnOutput(
            self,
            "superuser-task-definition-arn",
            value=superuser_task_definition.task_definition_arn,
        )
