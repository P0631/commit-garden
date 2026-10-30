.PHONY: test demo svg

test:
	python -m unittest discover -s tests -v

demo:
	rm -rf /tmp/garden-demo
	python -m commit_garden demo /tmp/garden-demo
	python -m commit_garden grow /tmp/garden-demo

svg:
	python -m commit_garden grow . -f svg -o assets/garden.svg
