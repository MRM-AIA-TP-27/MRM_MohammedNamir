 To create a new branch and immediately switch to it
git checkout -b Temp

 To add, commit, and push the new file to the 'Temp' branch
git add Task_3.md
git commit -m "Task 4: Add Task 3 description on Temp branch"
git push -u origin Temp

 To switch back to the 'main' branch
git checkout main

 To merge the commits from 'Temp' into 'main'
git merge Temp

 To add, commit, and push the final documentation to the 'main' branch
git add Task_4_5.md
git commit -m "Task 5: Add Task 4-5 description and merge Temp branch"
git push origin main

