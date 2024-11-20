
from flask import Flask, request, jsonify,render_template
import os,logging
from git_operations import *
import logging
from logger import logger

app = Flask(__name__)


# Route to get all repositories (for testing purposes)
@app.route('/repos', methods=['GET'])
def get_all_repos():
    # Fetch all repositories
    username, token = read_github_credentials()
    repositories = list_repositories_with_lastupdate(token)

    if isinstance(repositories, list):
        return jsonify(repositories)
    
@app.route('/add_repo',methods=['POST'])
def add_repo():
    data = request.get_json()
    username, token = read_github_credentials()
    repo_name = data.get('repo_name')
    local_path = data.get('local_path')
    base_branch= data.get('branch') if data.get('branch') else "develop"
    try:
        create_github_repo_and_connect_directory(repo_name,local_path,username,token),200
        logger.info(f"repo {repo_name} created")
        #copy_wp_git_ignore(local_path)
        logger.info(f"gitignore copied for repo {repo_name}")
        git_push_with_token(local_path,"CA","main",username,token,None,repo_name)
        logger.info(f"successfully push for {repo_name}")
        try:
            create_branch_and_change_default(repo_name,username,token,"develop",base_branch)
            logger.info(f"branch added! base branch is {base_branch} for {repo_name}")
        
        except:
            logger.info(f"branch Not added for {repo_name}")
        return jsonify(f"Successfully added repo!"),200
    except Exception as ex:
        logging.error(f"Error on creating github repo {repo_name} for path {local_path}. ERROR: {str(ex)}")
        return jsonify({"ERROR":f"Error on creating github repo {repo_name} for path {local_path}"}), 400



@app.route('/gitpush',methods=['POST'])
def gitpush():
    data = request.get_json()
    username, token = read_github_credentials()
    repo_name = data.get('repo_name')
    local_path = data.get('local_path')
    base_branch= data.get('branch') if data.get('branch') else "develop"
    try:
        git_push_with_token(local_path,"Commit Auto",base_branch,username,token,None,repo_name)
        return jsonify({"status":"success","message":f"successfully pushed dir {local_path} repo {repo_name} branch {base_branch}"})
    except Exception as ex:
        logger.error(f"ERROR on pushing for {repo_name} ERROR: {str(ex)}")
        return jsonify({"status":"error","message":f"unable to push"})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

