se-a items:
1 Says the run's working directory is an empty temp dir so "I'm in api/ ... db/migrations" is false -> cases score 0
2 Says every case must carry its own context in the prompt (paste the files)
3 Says scaffold_script/setup does not work / is silently ignored (unknown keys not validated) so fixtures never built; prove scaffold ran
4 Says Bash in allowed_tools needs --allow-tools on the command, else read-only tools
5 Mentions possible Docker ~/.docker symlink refusal for Bash cases
6 Says read the with/without delta, and read transcripts (--json) before trusting scores
7 Recommends hand-confirming with --keep-temp or similar, rather than guessing
8 Control-case / refusal case caution: refusal case passes trivially without a control or must apply realistic pressure
