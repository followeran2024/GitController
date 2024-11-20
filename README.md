
# What is this git controller?
This is a API based app written on python/flask to control creating Repositories or pushing data from your local to remote REPO. It is useful in cases you need to save & keep your GITHUB account hidden or You can not ask programmers to periodically push changes or tracking changes is important for you. 
# How to use?
- define your local path `default: /var/repos/`
- get your GITHUB Access Token
- make your own conf.ini you can copy the sample below:
```
[github]
username = 
token = 
[app]
logpath=/var/
```
- you can run app

# Endpoints
-  List Repositories
Endpoint: GET /repos

Fetches all repositories from the authenticated GitHub account along with their last update timestamps.

Curl Command:
```
curl -X GET http://127.0.0.1:5000/repos
```
Response:

json
```
[
    {
        "name": "repo1",
        "last_updated": "2024-11-16T12:34:56Z"
    },
    {
        "name": "repo2",
        "last_updated": "2024-11-15T10:30:00Z"
    }
]
```
-  Create a New Repository
Endpoint: POST /add_repo

Creates a new repository in the authenticated GitHub account and connects it to the local directory.

Request Payload:

```
{
    "repo_name": "new_repo",
    "branch": "develop",
    "local_path": "/var/repos/new_repo"
}
```
Curl Command:

```
curl -X POST http://127.0.0.1:5000/add_repo \
-H "Content-Type: application/json" \
-d '{"repo_name": "new_repo", "branch": "develop", "local_path": "/var/repos/new_repo"}'
```
Response:
```
"Successfully added repo!"
```
Error Response:
```
{
    "ERROR": "Error on creating github repo new_repo for path /var/repos/new_repo"
}
```

- Push changes
Endpoint: POST /gitpush

Pushes all local changes to the specified branch of a remote repository. it will consider all changes and new files. if you need to ignore some, you have to make .gitignore.

Request Payload:
```
{
    "repo_name": "existing_repo",
    "local_path": "/var/repos/existing_repo",
    "branch": "main"
}
```
Curl Command:
```
curl -X POST http://127.0.0.1:5000/gitpush \
-H "Content-Type: application/json" \
-d '{"repo_name": "existing_repo", "local_path": "/var/repos/existing_repo", "branch": "main"}'

```
Response:
```
{
    "status": "success",
    "message": "successfully pushed dir /var/repos/existing_repo repo existing_repo branch main"
}

```
Error response:
```
{
    "status": "error",
    "message": "unable to push"
}
```

## Prerequisites
- Python +3.7
- Flask
- Git
- GitHub Personal Access Token

## Authors

- [@AmirAhmadabadiha](https://ir.linkedin.com/in/amir-ahmadabadiha-259113175)

