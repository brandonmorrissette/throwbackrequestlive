To Do

-   Fix Login form sizing
-   Standardize stack inputs (project name and env are going to every single one. Standardize that. Probably don't need to pass ID for everyone. I THINK we can infer somehow.)
-             Clean up tagging a bit.
-   The deployment for the full app does not work. There is some unclear timing issue for the runtime stack. Every iteration some differnt exception pops up making it BRUTAL to troubleshoot.
-   Breakup all dependencies and use Param store and secrets manager for references
-   Clean up workflows and understand the matrix better
-   File by file analysis. I want to understand ever line of code and if it's needed AND best practice. Will review with AI.
-   Explore the ExecutionRole for StorageStack. I'd like a central Execution role but that is causing circular dependencies.
-   TESTING!!!
-   Much better password reset
