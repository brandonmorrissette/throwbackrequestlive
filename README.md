To Do

# Error handling and logging

-   Clean and consistent error handling/logging
    -   Cognito (maybe additional) services return appropriate failures to front end
-   Environment logging configuration

# Security

-   Update cognito_service to validate JWT

# Code Quality

-   File by file analysis. I want to understand ever line of code and if it's needed AND best practice. Will review with AI.
-   Code quality and testing

### Post MVP

# Improve Front End Skills

-   Learn React and other front end libraries used
    -   Context
    -   Proper modeling for AG Grid ColumnDefs and AG Grid in general
    -   Review DateTimeCellEditor
-   Group management for super user
    -   Roles in general? Review.
    -   Split groups from Cognito service. Probably split into multiple services.
-   additionalProps typing in DataManagement

# Cognito/User concepts cleanup

-   Cognito user updates
    -   superuser becomes site_admin
    -   admin becomes db_admin
-   Dynamic table properties for user flow (Currently hard coded)
-   Only Update Cognito users when there have been actual updates

# Data

-   Consider tables and data in an ETL context for future proofing (I don't remember what this means, but I THINK it means better modeling as OOP)
-   Support for Auto Incrementing
-   The write flow for rows feels off.
    -   Most of my data is passed to table from DataManagement, which uses the table service to interact with backend
    -   My table takes the data, and the data service. It then uses the service to write to the backend. Something about this feels weird.

# Data Management

-   Default datetime to something more user friendly. It defaults to the exact second of Now.

# Login

-   Fix Login form sizing
-   Login hangs on error
-   Much better password reset

# App UI

-   Footer covers up bottom still

# Docker

-   Break up front end and back end containers
    -   Consider breaking out postgress instance for local storage
