.PHONY: README.md
README.md:
	sed -i 's/\\usepackage{arxiv}/% \\usepackage{arxiv}/' anubis-design.tex
	pandoc -s --verbose --toc anubis-design.tex -o ../README.md
	sed -i 's/% \\usepackage{arxiv}/\\usepackage{arxiv}/' anubis-design.tex

	sed -i '1i <!-- -->' ../README.md
	sed -i '1i `pandoc -s --toc anubis-design.tex -o ../README.md`' ../README.md
	sed -i '1i [see anubis-design.pdf for offical](anubis-design.pdf)' ../README.md
	sed -i '1i Generated from doc/design-tex/anubis-design.tex using pandoc' ../README.md
	sed -i 's/figures\//design-tex\/figures\//g' ../README.md
	sed -i 's/{#.*}//g' ../README.md

.PHONY: anubis-design.pdf
anubis-design.pdf:
	latex -shell-escape  -output-format=pdf anubis-design.tex

clean:
	rm -rf _minted-* *.aux *.out *.log *.toc
