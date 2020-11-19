readme:
	hcl --help | pipe2codeblock README.md --tgt _help && \
	hcl --command "help" | pipe2codeblock README.md --tgt _commands

commands:
	mkdir -p commands && \
	rm -f commands/*.md && \
	hcl --command "help -s" | \
		xargs --max-procs 4 -I _ sh -c "printf '# _\n\n\`\`\`\n' > commands/_.md && hcl --command '_ --help' >> commands/_.md && echo '\`\`\`' >> commands/_.md"

docs: readme commands
