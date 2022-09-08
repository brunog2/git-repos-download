from os import listdir, chdir, makedirs, path, remove
from subprocess import run, call, check_output
from glob import glob
from shutil import rmtree
import urllib.request 
import json

dir_folders = path.expanduser('~')+'/Documents/projects/ntm-senai-2/'
if not path.exists(dir_folders): makedirs(dir_folders)
repos = []
page = 2

while True:
    remote_projects = urllib.request.Request(f'https://gitlab.com/api/v4/groups/ntm-senai/projects?per_page=100&page={page}')
    remote_projects.add_header('PRIVATE-TOKEN', 'glpat-HZhfPDaUjL_KwoCFsuUq')
    remote_projects = urllib.request.urlopen(remote_projects)
    response = json.loads(remote_projects.read().decode())
    if response:
        repos += response
        page += 1
    break



for repo in repos:
    repoURL = repo['ssh_url_to_repo']
    repoPath = repo['path']
    repoFolder = repoPath
    print(f'Clonning repo #{repos.index(repo)+1}')

    # clone repo
    try:
        cloneRepo = f'git clone {repoURL} {dir_folders+repoFolder}'.split()
        run(cloneRepo)
    
    except Exception as cloneException:
        print(cloneException)


    # fetch, create and update branches
    # fetchBranches = "for b in `git branch -r | grep -v -- '->'`; do git branch --track ${b##origin/} $b; done".split()
    try:
        chdir(dir_folders+repoFolder)    
        remoteBranches = [x.decode('utf-8') for x in check_output("git branch -r".split()).split()]
        if 'origin/HEAD' in remoteBranches: remoteBranches.remove('origin/HEAD')
        if '->' in remoteBranches: remoteBranches.remove('->')
        
        for branch in remoteBranches:
            replicateBranch = f'git branch --track {branch}'.split()
            run(replicateBranch)
        
        # update local branches
        updateBranches = f'git fetch --all'.split()
        run(updateBranches)

    except Exception as fetchException:
        print(fetchException)

    # zip repo folder
    try:
        zipRepo = f'zip -r {dir_folders+repoPath}.zip'.split()
        call(zipRepo+glob(dir_folders+repoPath))

        # remove folder
        rmtree(dir_folders+repoPath)

        chdir(dir_folders)    
    
    except Exception as zipException:
        print(zipException)

    
# get all remote repos
# for repo in repos:
#     if repo['path'] not in dir_folders:
#         print(repo)

