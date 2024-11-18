from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class SuperuserConstruct(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.superuser_secret = secretsmanager.Secret(
            self, "SuperuserSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "superuser"}',
                generate_string_key="password",
                password_length=16,
                exclude_punctuation=False,
            ),
            description="Superuser credentials for superuser access",
        )
