Python 3
Install requirements (preferably in a venv)
You need git and hg installed.
You also need hg-fast-export somewhere (clone https://github.com/frej/fast-export.git)
Mercurial repositories must not have "unnamed heads" like closed unnamed branches. You can create a branch on each such head to solve that:
 - hg heads -c  # to list
 - for each "branch end" revision:
    hg update -r $REV
    hg branch r${REV}-fix-git-conversion
    hg commit -m "Fix git conversion (unnamed head)"
    hg update default
    hg push --new-branch


Update the 5 variables at the top of the script and just run it.
It will convert all your hg repos (by creating new git ones)
It has no resume capability, so if something fails and you fix it, you must delete previously created repos manually to rerun