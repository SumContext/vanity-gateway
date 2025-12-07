
sumtree produces output similar to the tree command, but adds file 
summaries from LLMs next to each filename.


### Currently works!

`tree.sums.json` is produced in the target dir - saving summaries

in `cog_cfg.json` add gitignore style descriptions of files you don't want sent over the internet:

gignore json:

```json
    "gignore": ".git/\n*.key"
```

## current issues

We're setting up this repository to act as a flake.


## Future Functinality

### SumIssueSumFile

`SumIssueSumFile(issue, file, target_dir)`
list the sumtree output, the issue we are working on, and the entire 
current file, along with a json yes/no dialog for if the current file 
is pertinent to our issue; returns true or false
