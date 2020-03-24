LAB = bomblab

all:
	latex $(LAB).tex
	latex $(LAB).tex # again to resolve references
	dvips -o $(LAB).ps -t letter $(LAB).dvi
	ps2pdf $(LAB).ps

clean:
	rm -f *.aux *.ps *.pdf *.dvi *.log *~


