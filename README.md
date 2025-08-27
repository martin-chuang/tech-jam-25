# Tiktok Tech Jam 2025
## Topic 7: Privacy for AI

## Installation quick start
Step 1: Clone repository<br>
Step 2: Create virtual env<br>
Step 3: Enter virtual env<br>
Step 4: Install packages from requirements.txt<br>
Step 5: Ensure project can be executed (main.py)<br>

## Version Control
Step 1: Create branch from local<br>
`git checkout branch_name`
Step 2: Make code edits<br>
Step 3: Once done, commit and push changes to remote branch<br>
```
git add .
git commit -m "Commit message"
git push origin branch_name
Check that changes to the branch are shown on github
```
Step 4: Go to local main branch and merge from branch_name<br>
```
git checkout main
git fetch origin
git merge origin/branch_name
```
Step 5: Push new changes to remote main<br>
`git push origin main`
Step 6: Delete remote and main branch_name (Optional)<br>
```
git branch -d branch_name
git push origin --delete branch_name`
```