import os
import subprocess,requests
import configparser
from git import Repo
from urllib.parse import quote
import logging
from logger import *
def copy_wp_git_ignore(repo_path):
    os.system(f"cp .gitignore {repo_path}")
def configure_remote_repo(local_dir, github_username, personal_access_token, repo_name):
    """
    Adds a remote origin to a local Git repository using a Personal Access Token (PAT).

    :param local_dir: Local repository directory
    :param github_username: GitHub username
    :param personal_access_token: GitHub Personal Access Token
    :param repo_name: GitHub repository name
    """
    if not os.path.exists(local_dir):
        print(f"Error: Directory '{local_dir}' does not exist.")
        return

    # URL-encode the token to handle special characters
    encoded_token = quote(personal_access_token)

    # Construct the HTTPS remote URL with credentials
    clone_url = f"https://{github_username}:{encoded_token}@github.com/{github_username}/{repo_name}.git"

    try:
        # Initialize Git repository if not already done
        subprocess.run(["git", "-C", local_dir, "init"], check=True)

        # Check if remote origin already exists, and remove if necessary
        subprocess.run(["git", "-C", local_dir, "remote", "remove", "origin"], check=False)

        # Add the remote origin with credentials
        subprocess.run(["git", "-C", local_dir, "remote", "add", "origin", clone_url], check=True)

        print(f"Remote repository '{repo_name}' added successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during Git operation: {e}")

# Function to create a new repository on GitHub
def create_github_repo(repo_name, github_username, github_token):
    url = f"https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "auto_init": True,  # Initialize with a README file (optional)
        "private": False     # Set to True if you want to create a private repo
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print(f"Successfully created the repository {repo_name} on GitHub.")
    else:
        print(response.text)
        raise Exception(f"Failed to create GitHub repository: {response.json()['message']}")



# Read GitHub credentials from conf.ini
def read_github_credentials(config_path="conf.ini"):
    config = configparser.ConfigParser()
    config.read(config_path)

    # Retrieve GitHub credentials
    username = config.get("github", "username")
    token = config.get("github", "token")

    if not username or not token:
        raise ValueError("GitHub username or token is missing in the configuration file.")
    
    return username, token

# Initialize Git repo if needed
def init_git_repo(repo_path):
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
    try:
        repo = Repo.init(repo_path)
        return repo
    except Exception as e:
        raise Exception(f"Error initializing git repository: {e}")

# Clone a repository
def clone_repo(repo_url, repo_path, username, token):
    if os.path.exists(repo_path):
        raise FileExistsError(f"Directory {repo_path} already exists.")
    try:
        # Clone using HTTPS and basic auth (using token as password)
        repo_url_with_token = repo_url.replace("https://", f"https://{username}:{token}@")
        Repo.clone_from(repo_url_with_token, repo_path)
    except Exception as e:
        raise Exception(f"Error cloning repository: {e}")

# Add a remote repository section to conf.ini
def add_repo_to_conf(config_path, repo_name, repo_url, local_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    # Add the new repo section
    section_name = f"repo_{repo_name}"
    if section_name not in config.sections():
        config.add_section(section_name)
    
    config.set(section_name, 'repo_url', repo_url)
    config.set(section_name, 'local_path', local_path)

    with open(config_path, 'w') as configfile:
        config.write(configfile)

    return section_name

# Check if directory is a git repo
def is_git_repo(repo_path):
    return os.path.exists(os.path.join(repo_path, ".git"))



def list_repositories(access_token):
    """
    Fetches a list of all repositories in your GitHub account using a Personal Access Token.

    :param access_token: GitHub Personal Access Token
    :return: List of repository names or an error message
    """
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = "https://api.github.com/user/repos"
    repos = []
    page = 1

    try:
        while True:
            # Paginate through repositories
            response = requests.get(url, headers=headers, params={"per_page": 100, "page": page})
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break
                repos.extend([repo["name"] for repo in data])
                page += 1
            else:
                return f"Error: {response.status_code} - {response.json().get('message', 'Unknown error')}"

        return repos
    except Exception as e:
        return f"An error occurred: {str(e)}"

def list_repositories_with_lastupdate(access_token):
    """
    Fetches a list of all repositories in your GitHub account using a Personal Access Token,
    including the last update timestamp.

    :param access_token: GitHub Personal Access Token
    :return: List of dictionaries containing repository names and last update timestamps,
             or an error message.
    """
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = "https://api.github.com/user/repos"
    repos = []
    page = 1

    try:
        while True:
            # Paginate through repositories
            response = requests.get(url, headers=headers, params={"per_page": 100, "page": page})
            if response.status_code == 200:
                data = response.json()
                if not data:  # Exit loop if no more data
                    break

                # Collect repo name and last update timestamp
                repos.extend([{"name": repo["name"], "last_updated": repo["updated_at"]} for repo in data])
                page += 1
            else:
                return f"Error: {response.status_code} - {response.json().get('message', 'Unknown error')}"

        return repos
    except Exception as e:
        return f"An error occurred: {str(e)}"


def create_github_repo_and_connect_directory(repo_name, local_dir, github_username, personal_access_token):
    """
    Creates a GitHub repository and connects a local directory to it.

    :param repo_name: Name of the GitHub repository to create
    :param local_dir: Path to the local directory to connect
    :param github_username: GitHub username
    :param personal_access_token: GitHub Personal Access Token with `repo` permissions
    """
    # GitHub API URL for creating a repository
    api_url = "https://api.github.com/user/repos"
    
    # Repository creation payload
    payload = {
        "name": repo_name.strip(),  # Strip any leading/trailing whitespace
        "private": True  # Set to False for a public repository
    }
    
    # Headers with authentication
    headers = {
        "Authorization": f"token {personal_access_token}"
    }
    
    # Create the GitHub repository
    response = requests.post(api_url, json=payload, headers=headers)
    
    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully!")
        repo_url = response.json()["html_url"]
        clone_url = response.json()["clone_url"]
        print("CLONURL_BEFORE",clone_url)
        clone_url=f"https://{github_username}:{personal_access_token}@github.com/{github_username}/{repo_name}.git"
    elif response.status_code == 422:
        print(f"Failed to create repository: {response.json().get('message')}")
        if "errors" in response.json():
            for error in response.json()["errors"]:
                print(f"Error: {error.get('message')}")
        return
    else:
        
        print(f"Unexpected error ({response.status_code}): {response.text}")
        return
    
    # Ensure the local directory exists
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    # Initialize a local git repository and connect it to GitHub
    try:
        copy_wp_git_ignore(local_dir)
        subprocess.run(["git", "-C", local_dir, "init"], check=True)
        subprocess.run(["git", "-C", local_dir, "remote", "add", "origin", clone_url], check=True)
        print(f"Connected local directory '{local_dir}' to '{repo_url}'")
        #git_push(local_dir,"initial","main")
        logger.info(f"initial commit has done for {repo_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up git in the directory: {e}")
#create_github_repo_and_connect_directory("TEST","/home/amir/Documents/tst","x","x")


def create_branch_and_change_default(repo_name, github_username, personal_access_token, new_branch_name, base_branch="main"):
    """
    Creates a new branch and sets it as the default branch on GitHub.

    :param repo_name: The name of the repository
    :param github_username: GitHub username
    :param personal_access_token: GitHub Personal Access Token
    :param new_branch_name: The name of the new branch to create
    :param base_branch: The branch from which the new branch will be created (default is 'main')
    """
    # GitHub API URLs
    repo_api_url = f"https://api.github.com/repos/{github_username}/{repo_name}"
    branches_url = f"{repo_api_url}/git/refs"
    default_branch_url = f"{repo_api_url}"

    # Headers with authentication
    headers = {
        "Authorization": f"token {personal_access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Step 1: Ensure the base branch exists
    response = requests.get(f"{branches_url}/heads/{base_branch}", headers=headers)
    if response.status_code == 200:
        base_branch_sha = response.json()["object"]["sha"]
        print(f"Base branch '{base_branch}' found with SHA {base_branch_sha}.")
    else:
        # If base branch does not exist, create it based on the repository's default branch
        print(f"Base branch '{base_branch}' not found. Attempting to create it.")
        default_branch_response = requests.get(f"{branches_url}/heads/main", headers=headers)
        if default_branch_response.status_code == 200:
            base_branch_sha = default_branch_response.json()["object"]["sha"]
            create_base_payload = {
                "ref": f"refs/heads/{base_branch}",
                "sha": base_branch_sha
            }
            create_base_response = requests.post(branches_url, json=create_base_payload, headers=headers)
            if create_base_response.status_code == 201:
                print(f"Base branch '{base_branch}' created successfully.")
            else:
                print(f"Failed to create base branch '{base_branch}': {create_base_response.json().get('message')}")
                return
        else:
            print(f"Failed to find or create base branch '{base_branch}': {default_branch_response.json().get('message')}")
            return

    # Step 2: Create the new branch
    payload = {
        "ref": f"refs/heads/{new_branch_name}",
        "sha": base_branch_sha
    }
    response = requests.post(branches_url, json=payload, headers=headers)
    if response.status_code == 201:
        print(f"Branch '{new_branch_name}' created successfully!")
    else:
        print(f"Failed to create branch: {response.json().get('message')}")
        return

    # Step 3: Change the default branch to the new branch
    payload = {
        "default_branch": new_branch_name
    }
    response = requests.patch(default_branch_url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Default branch changed to '{new_branch_name}' successfully!")
    else:
        print(f"Failed to change default branch: {response.json().get('message')}")



def git_push(local_dir, commit_message="auto commit", branch="main"):
    """
    Pushes local changes to the remote repository.

    :param local_dir: Path to the local directory with the repository
    :param commit_message: Commit message for the changes
    :param branch: Branch to push to (default is 'main')
    """
    if not os.path.exists(local_dir):
        print(f"Error: Directory '{local_dir}' does not exist.")
        return

    try:
        # Step 1: Initialize the repository if not already done
        subprocess.run(["git", "-C", local_dir, "init"], check=True)

        # Step 2: Check if the repository has any commits
        result = subprocess.run(
            ["git", "-C", local_dir, "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            text=True,
        )

        # Step 3: Add all changes to the staging area
        subprocess.run(["git", "-C", local_dir, "add", "."], check=True)

        # Step 4: Make the initial commit if no commits exist
        try:
            subprocess.run(["git", "-C", local_dir, "log"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("No commits found. Creating the initial commit.")
            subprocess.run(["git", "-C", local_dir, "commit", "-m", "Initial commit"], check=True)

        # Step 5: Set the branch if not set
        subprocess.run(["git", "-C", local_dir, "branch", "-M", branch], check=True)

        # Step 6: Push changes to the remote repository
        subprocess.run(["git", "-C", local_dir, "push", "-u", "origin", branch], check=True)

        print(f"Changes pushed to branch '{branch}' successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operation: {e.stderr}")


def git_push_with_token(local_dir, commit_message, branch="main", github_username=None, personal_access_token=None, remote_url=None,repo_name=None):
    """
    Pushes local changes to the remote repository with token-based authentication.

    :param local_dir: Path to the local directory with the repository
    :param commit_message: Commit message for the changes
    :param branch: Branch to push to (default is 'main')
    :param github_username: GitHub username
    :param personal_access_token: GitHub Personal Access Token
    :param remote_url: Remote repository URL (if not provided, constructed from username and token)
    """
    if not os.path.exists(local_dir):
        print(f"Error: Directory '{local_dir}' does not exist.")
        return

    if not github_username or not personal_access_token:
        print("Error: GitHub username and Personal Access Token are required.")
        return

    # Construct the remote URL with token if not provided
    if not remote_url:
        repo_name = repo_name if repo_name else os.path.basename(local_dir.rstrip('/'))  # Get repo name from directory
        remote_url = f"https://{github_username}:{personal_access_token}@github.com/{github_username}/{repo_name}.git"

    try:
        # Step 1: Initialize the repository if not already initialized
        subprocess.run(["git", "-C", local_dir, "init"], check=True)

        # Step 2: Set the remote URL if not already set
        subprocess.run(["git", "-C", local_dir, "remote", "add", "origin", remote_url], check=False)

        # Step 3: Add all changes to the staging area
        subprocess.run(["git", "-C", local_dir, "add", "."], check=True)

        # Step 4: Commit changes if there are any
        commit_result = subprocess.run(
            ["git", "-C", local_dir, "commit", "-m", commit_message],
            check=False,
            capture_output=True
        )

        if commit_result.returncode == 0:
            print(f"Changes committed with message: '{commit_message}'")
        else:
            # If no changes to commit, `git commit` returns a non-zero exit code
            print("No changes to commit. Skipping commit step.")

        # Step 5: Set the branch (if needed)
        subprocess.run(["git", "-C", local_dir, "branch", "-M", branch], check=True)

        # Step 6: Push changes to the remote repository
        subprocess.run(["git", "-C", local_dir, "push", "-u", "origin", branch], check=True)

        print(f"Changes pushed to branch '{branch}' successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operation: {e.stderr.decode().strip()}")
