import aws_cdk as cdk


class Config:
    def __init__(
        self,
        project_name: str | None,
        environment_name: str | None,
        cdk_environment: cdk.Environment | None,
    ) -> None:
        self.project_name = project_name
        self.environment_name = environment_name
        self.cdk_environment = cdk_environment

    def __str__(self) -> str:
        return f"Config(project_name={self.project_name}, environment_name={self.environment_name}, cdk_environment={self.cdk_environment})"
