SRC = McFeeNieto-ISMIR2015

all: $(SRC).tex
	pdflatex $<
	bibtex $(SRC)
	pdflatex $<
	pdflatex $<

check: $(SRC).tex
	chktex $<
	ispell -t $<

gray: $(SRC).pdf
	pdf2ps -sDEVICE=psgray $(SRC).pdf - |ps2pdf - $(SRC)-gray.pdf


clean:
	rm -f *.aux *.log *.out

spotless: clean
	rm -f *.dvi *.bak *.bbl *.blg
