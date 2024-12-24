To Do

-   Table Serialization
-   BIG naming refactor.
    -   superuser becomes site_admin
    -   admin becomes db_admin
    -   the routes in the front end should closely align with the routes in the backend, without exposing implementation
-   The deployment for the full app does not work. There is some unclear timing issue for the runtime stack. Every iteration some differnt exception pops up making it BRUTAL to troubleshoot.
    -   I want to use docker-compose and isolate the front end and the back end deployments completely
-   Standardize stack inputs (project name and env are going to every single one. Standardize that. Probably don't need to pass ID for everyone. I THINK we can infer somehow.)
-   Clean up stack tagging a bit.
-   Design correct pattern for depenency management bettwen stacks
-   Clean and consistent error handling/logging
    -   Cognito (maybe additional) services return appropriate failures to front end
-   File by file analysis. I want to understand ever line of code and if it's needed AND best practice. Will review with AI.
-   Code quality and testing
-   Explore the ExecutionRole for StorageStack. I'd like a central Execution role but that is causing circular dependencies.
-   Learn React
    -   Context
-   Footer covers up bottom still
-   Update cognito_service to validate JWT
-   Much better password reset
-   Group management for super user
    -   Roles in general? Review.
    -   Split groups from Cognito service. Probably split into multiple services.
-   Explore removing boto3 from user_pool construct. Or at least isolate it there.
-   Fix Login form sizing
-   Login hangs on error
-   Consider tables and data in an ETL context for future proofing
-   Break up front end and back end containers
    -   Consider breaking out postgress instance for local storage
-   DRY in the cognito and data services with SQLAlchemy. It's small enough I don't know if I care, but feels like something that could grow.
-   additionalProps typing in DataManagement
-   Dynamic table properties for user flow
-   Production logging
-   Only Update Cognito users when there have been actual updates
