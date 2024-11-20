import configparser
import requests

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

# Authenticate with GitHub using the credentials (token-based auth)
def github_login(username, token):
    # GitHub API URL to verify authentication
    url = "https://api.github.com/user"
    
    # Make a GET request to GitHub API using basic authentication
    response = requests.get(url, auth=(username, token))

    # Check if authentication was successful
    if response.status_code == 200:
        print(f"Authenticated successfully as {username}")
        return True
    else:
        print(f"Authentication failed: {response.status_code} - {response.text}")
        return False

# Example usage
if __name__ == "__main__":
    try:
        username, token = read_github_credentials()
        if github_login(username, token):
            print("Login successful!")
        else:
            print("Login failed!")
    except Exception as e:
        print(f"Error: {e}")
