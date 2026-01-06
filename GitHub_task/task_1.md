# To create the project directory
mkdir GitHub_task
cd GitHub_task

# To initialize a new Git repository
git init

# To stage all files for the first commit
git add .

# To save the staged changes with a message
git commit -m "Task 1: Add hello world program"

# To ensure the primary branch is named 'main'
git branch -M main

# To link the local folder to the remote repository on GitHub
git remote add origin <your-repository-url>

# To upload the local commits to the remote repository
git push -u origin main
