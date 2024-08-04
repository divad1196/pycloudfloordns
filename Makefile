.PHONY: docs
docs:
	# See Pdoc for documentation generation
	# public contains gitlab's pages
	# https://docs.gitlab.com/ee/user/project/pages/#how-it-works
	python3.10 -m pdoc ./cloudfloordns/ -o ./public/

.PHONY: isolate
isolate:
	docker run -it --rm -w '/workdir' -v "$$PWD:/workdir" python:3.9 bash
	# NOTE: You might want to run the following in the container:
	#	# Allow using git based on the active directory (necessary for pre-commit)
	# 	- git config --global --add safe.directory /workdir
	# 	- pip install pre-commit poetry
