
# RLC - Run Log Concat

Vibe coding development environment.

The heart of RLC is `concat_macro.sh` everything else is icing on the 
cake or documentation and gui helper apps or macros to assist in using 
`concat_macro.sh`

`concat_macro.sh` creating a semi-reproducible log of the problem at 
hand. There is still non deterministic things like time and system 
information. but that might be pertinent to the current issue, like 
process `X` takes this long or we're having trouble with hardware `Y`.

## Issue Management

The whole idea of RLC is to create a prompt for a developer and/or an 
LLM where they can read the logs of the problem at hand, and the files 
that are pertinent to  the issue.

And either work on the solution immediately or ask for more information.

## task list / tracking

every Issue will have a task List

the 1st job will be RLC itself and it's executor should be 
`current-system` but we may set that up to be `remote-systems` later

task-List:

|name|executor|
|RLC|current-system|
|summarization|JuniorLM|
|cut-out|JuniorLM and User|
|diagnostics|SeniorLM|
|patching|JuniorLM on the output from the SeniorLM|

## json
The task list will be json.


## issue.md

280 chars or less Summaries

Summaries for groups of files, entire dirs, or individual files.

Files that might be pertinent should have ther own summary, if their 
entire text is included in the issue.md there should be no summary 
provided.

other files like icons and other doodads should be moved to a dir like 
`/rsrcs` and a summary of the folder should be included.

again the goal is shortening our issue.md so if the whole file is 
included we don't need a summary, but if we really need just 1 
function out of it we might do a partial include, and the summary.

most of the work is designed to be done by a junior developer, where 
diagnostics and patching should be set up so if there is trouble at 
that stage the people doing the work will be saying something like can 
you give me the whole file `Z`.

Remember we're trying to conserve bandwidth on this channel, so we can 
use more tokens for solving other issues. The entities doing 
diagnostics and patching shouldn't see any of this unless they are 
working on RLC.

## cut-out gui

There will be a file list, where the user and the JuniorLM will vote 
on what files should be included in the issue. only the user votes 
will count, but they should view the JuniorLM votes and summaries will 
also be shown to the user here to influence their decision making 
process so they can work faster.

## Branch Management

Each Issue should have a unique number, and the response from the 
issue.md being given to the SeniorLM should be parsed by the JuniorLM 
to create and apply the patch.

When a patch is a applied it will create a new branch, possibly new issues 

In the event the issue isn't solved, 
