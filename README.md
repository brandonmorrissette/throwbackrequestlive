To Do

-   BIG naming refactor.
    -   votes becomes requests
    -   superuser becomes site_admin
    -   admin becomes db_admin
-   -   Fix Login form sizing
-   The deployment for the full app does not work. There is some unclear timing issue for the runtime stack. Every iteration some differnt exception pops up making it BRUTAL to troubleshoot.
-   Standardize stack inputs (project name and env are going to every single one. Standardize that. Probably don't need to pass ID for everyone. I THINK we can infer somehow.)
-                                       Clean up tagging a bit.

-   Design correct pattern for depenency management bettwen stacks
-   File by file analysis. I want to understand ever line of code and if it's needed AND best practice. Will review with AI.
-   Explore the ExecutionRole for StorageStack. I'd like a central Execution role but that is causing circular dependencies.
-   TESTING!!!
-   Update cognito_service to validate JWT
-   Much better password reset
-   Group management for super user
-   Explore removing boto3 from user_pool construct. Or at least isolate it there.
-   Login hangs on error
