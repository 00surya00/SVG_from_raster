make:
	./main.py
output:
	feh *.png
edit:
	vi main.py
clean:
	rm -rf sum_of_all_paths* path* canny* enhanced*
