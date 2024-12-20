To Do

-   Table assumes data service behind it. Need to solve a way
    for dependency injection to swap the data service and user service
-   BIG naming refactor.
    -   superuser becomes site_admin
    -   admin becomes db_admin
    -   the routes in the front end should closely align with the routes in the backend, without exposing implementation
-   The deployment for the full app does not work. There is some unclear timing issue for the runtime stack. Every iteration some differnt exception pops up making it BRUTAL to troubleshoot.
-   Standardize stack inputs (project name and env are going to every single one. Standardize that. Probably don't need to pass ID for everyone. I THINK we can infer somehow.)
-   Clean up tagging a bit.
-   Design correct pattern for depenency management bettwen stacks
-   Clean and consistent error handling/logging
-   File by file analysis. I want to understand ever line of code and if it's needed AND best practice. Will review with AI.
-   Code quality and testing
-   Explore the ExecutionRole for StorageStack. I'd like a central Execution role but that is causing circular dependencies.
-   Footer covers up bottom still
-   Update cognito_service to validate JWT
-   Cognito users are returned to front end, not whatever object I created?
-   Much better password reset
-   Group management for super user
    -   Roles in general? Review.
-   Explore removing boto3 from user_pool construct. Or at least isolate it there.
-   Fix Login form sizing
-   Login hangs on error
-   Consider tables and data in an ETL context for future proofing
