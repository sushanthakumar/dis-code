# scn-p1-discovery

# Guidelines for DevelopmentTeam
Branching Strategy:

- Developer-Specific Branch: Each developer works on their own branch
- "Dev" Branch: branch where stable and tested code is merged.

## Best Practices – PR Submission

- Provide Meaningful Commit Messages that describe the specific changes in each commit
- Provide a Brief and Descriptive Title
- Properly filled template with all required information
- Additional information to support the review (including screenshots, logs and test reports)
- Every pull request has to be associated with at least one issue.
- Use appropriate labels to categorize the PR.
- Verify that all automated checks (linting, unit tests etc.) pass before submitting the PR. 

## Best Practices – PR Review and approval

- Check all information available for PRs (No test report or in sufficient information, please return the PRs)
- LGTM for approvals.
- Leave comments directly on the code wherever applicable. 


## Best Practices – Issue Submission

- Properly filled template with all required information
- Provide a Brief and Descriptive Title.
- Additional information to support verification or fixing the issues (including screenshots, logs and reports)
- Specify the version information on which the issue is being raised
- Use appropriate labels to categorize the issue
- Create subtasks as needed

## Best Practices – Issue Review and Fixing

- Review whether sufficient information is available?
- Reproducible on the similar test environment? (or discuss/review with submitter)
- Leave comments directly on the code wherever applicable 
- Address any questions or feedback from reviewers in a clearly and promptly


## Do’s and Don’ts

# Do’s 
- Follow the pull request and issue templates
- Associate every pull request with at least one issue
- If not applicable do not delete the checklist items in the template instead add N.A
- Merge only if the “status checks” are  passed

# Don’ts
- Submit a PR with large changes.
- Merge a PR without sufficient reviews and approvals.
- Merge a PR if automated checks have failed.
- Merge own PRs
