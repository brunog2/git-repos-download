from os import listdir, chdir, makedirs, path.expanduser
from subprocess import run, call, check_output
from glob import glob
from multiprocessing import cpu_count
import urllib.request 
import json
import queue
import threading as t

def downloadRepos(q):
    while True:
        dir_folders = path.expanduser('~')+'/Documents/git-repos'
        os.makedirs(dir_folders)
        repo = q.get()
        repoURL = repo['ssh_url_to_repo']
        repoPath = repo['path']
        repoFolder = repoPath
        
        # clone repo
        cloneRepo = f'git clone {repoURL} {dir_folders+repoFolder}'.split()
        run(cloneRepo)

        # fetch, create and update branches
        # fetchBranches = "for b in `git branch -r | grep -v -- '->'`; do git branch --track ${b##origin/} $b; done".split()
        chdir(dir_folders+repoFolder)    
        remoteBranches = [x.decode('utf-8') for x in check_output("git branch -r".split()).split()]
        remoteBranches.remove('origin/HEAD')
        remoteBranches.remove('->')
        
        for branch in remoteBranches:
            replicateBranch = f'git branch --track {branch}'.split()
            run(replicateBranch)
        
        # update local branches
        updateBranches = f'git fetch --all'.split()
        run(updateBranches)

        # zip repo folder and delete folder
        zipRepo = f'zip -r {dir_folders+repoPath}.zip'.split()
        call(zipRepo+glob(dir_folders+repoPath))

        # remove folder
        os.remove(dir_folders+repoPath)
        
        

    # get all remote repos
    # for repo in repos:
    #     if repo['path'] not in dir_folders:
    #         print(repo)


repos = []
page = 1

while True:
    remote_projects = urllib.request.Request(f'https://gitlab.com/api/v4/groups/ntm-senai/projects?per_page=100&page={page}')
    remote_projects.add_header('PRIVATE-TOKEN', 'glpat-HZhfPDaUjL_KwoCFsuUq')
    remote_projects = urllib.request.urlopen(remote_projects)
    response = json.loads(remote_projects.read().decode())
    if response:
        repos += response
        page += 1
    break

q = queue.Queue()
cpus = cpu_count() if cpu_count() <= 8 else 8

for i in range(cpus):
    worker = t.Thread(target=downloadRepos, args=(q,), daemon=True)
    worker.start()

for repo in repos:
    q.put(repo)

q.join()