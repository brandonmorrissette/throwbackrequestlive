To Do

# Code Quality

-   File by file analysis. I want to understand ever line of code and if it's needed AND best practice. Will review with AI.
    -   rdsConstruct
        -   adminRole being used? Is this how it should be handled?
    -   runtime_ecs
        -   explore if I must expose the load balancer. Feels weird.
-   Code quality and testing

### Post MVP

# Routing

-   route_53
    -   Remove hard coding. Find better way to pass or config.

# Improve Front End Skills

-   Learn React and other front end libraries used
    -   Context
    -   Proper modeling for AG Grid ColumnDefs and AG Grid in general
    -   Review DateTimeCellEditor
-   additionalProps typing in DataManagement

# Cognito/User concepts cleanup

-   Dynamic table properties for user flow (Currently hard coded)
-   Only Update Cognito users when there have been actual updates

# Data

-   Consider tables and data in an ETL context for future proofing (I don't remember what this means, but I THINK it means better modeling as OOP)
-   The write flow for rows feels off.
    -   Most of my data is passed to table from DataManagement, which uses the table service to interact with backend
    -   My table takes the data, and the data service. It then uses the service to write to the backend. Something about this feels weird.

# Data Management

-   Default datetime to something more user friendly. It defaults to the exact second of Now.

# App UI

-   Footer covers up bottom still

# Docker

-   Break up front end and back end containers
    -   Consider breaking out postgress instance for local storage
