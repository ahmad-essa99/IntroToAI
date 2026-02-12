.PHONY: run example

example:
	python -m  main --input inputs/example_input_file.txt --print-limit 200 --sims 2

run:
	python -m  main --input inputs/$(INPUT)