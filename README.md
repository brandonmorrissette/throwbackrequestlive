To Do

# Routing

-   route_53
    -   Remove hard coding. Find better way to pass or config.
-   unknown paths are not routing to main
-   Reconsider my API paths.
    -   I am trying to create a disctinction betweeen "table" routes and "row" routes. Also feels like a bad idea to need tables at every endpoiont? Clean that up.
        -   Table service. This handles tables at large.
        -   Data service. Handles "pieces" of data? Considering RowService as well.
        -   Use case specific services for handling "special" endpoints

# Infra

-   I have a better understanding of roles and policies now and wish to handle this with much better practice.
-   Remove db variable dependency from runtime. Resolve via ssm.

# Docker

-   Break up front end and back end containers
    -   Consider breaking out postgress instance for local storage

# Cognito/User concepts cleanup

-   Runtime and Cognito are tightly coupled. Somehow deploying Runtime really messes up User-DataManagement
    -   At this point they belong in different projects. Will move user-management out to it's own project referenced using boto.
-   Dynamic table properties for user flow (Currently hard coded)
-   Want a much better super user creation process
    -   Current task has some assumptions in the code and is inflexible.
-   Only Update Cognito users when there have been actual updates

# SQL Deployment

-   Externalize the tasks for deploying SQL from the storage.
    -   Think about these responsibilities, what resources are needed and whose responsibility that is. Too tightly coupled currently.

# Data

-   Consider tables and data in an ETL context for future proofing (I don't remember what this means, but I THINK it means better modeling as OOP)
-   Make a distinction between writing table and writing rows. Probably different classes?
-   table name in get rows is f-string. I'd rather bind to the query somehow to hijack some
    sql alchemy inject protection. Need to solve.

# Table component

-   Default datetime to something more user friendly. It defaults to the exact second of Now.
-   Reconsider fancy UI datetime element. I think the OOB is actually going to be better.
-   Proper modeling for AG Grid ColumnDefs and AG Grid in general

# SSM

-   Find a more central way of resolving ssm params in backend

# Improve Front End Skills

-   Fix collapsing/transition for navbar (Bootstrap)
-   Learn React and other front end libraries used
    -   Context

# App UI

-   Footer covers up bottom still

# Login

-   The login, login form and password reset could benefit from some better seperation of concerns.
-   The login form should take lessons learned from create show
