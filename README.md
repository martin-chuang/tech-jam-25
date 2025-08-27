# Tiktok Tech Jam 2025
## Topic 7: Privacy for AI

## Installation quick start
Step 1: Clone repository <br>
Step 2: Create virtual env <br>
Step 3: Enter virtual env <br>
Step 4: Install packages from requirements.txt <br>
Step 5: Ensure project can be executed (main.py) <br>

## Version Control
Step 1: Create branch from local
&emsp;git checkout branch_name
Step 2: Make code edits
Step 3: Once done, commit and push changes to remote branch
&emsp;git add .
&emsp;git commit -m "Commit message"
&emsp;git push origin branch_name
&emsp;Check that changes to the branch are shown on github
Step 4: Go to local main branch and merge from branch_name
&emsp;git checkout main
&emsp;git fetch origin
&emsp;git merge origin/branch_name
Step 5: Push new changes to remote main
&emsp;git push origin main
Step 6: Delete remote and main branch_name (Optional)
&emsp;git branch -d branch_name
&emsp;git push origin --delete branch_name