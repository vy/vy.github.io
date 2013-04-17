---
kind: article
created_at: 2012-04-28 03:53 EET
title: Build Scripts for LaTeX-BibTeX-XFig-GnuPlot Combo 
tags:
  - latex
---

Over the past 8 years, I needed to compile LaTeX documents for this or that reason. As time passed, I enhanced them with BibTeX, XFig, and Gnuplot. Further, I generally needed to produce PDF files validated by [IEEE PDF eXpress](http://www.pdf-express.org/). Here, I share some scripts I developed during the road to ease the pain.

First, note that there is a certain directory structure I stick to.

- `/` -- LaTeX (.tex) and BibTeX (`.bib`) files are placed here.
- `/constants.tex` -- LaTeX file for constants (variables, definitions, commands, etc.) shared between LaTeX and XFig files.
- `/make.sh` -- Compiles the whole project.
- `/figs` -- XFig (`.fig`), Gnuplot (`.gnu`), and EPS (`.eps`) files go here.
- `/figs/fig2eps.sh`
- `/figs/make.sh` -- Compiles the XFig and Gnuplot into EPS format.

Below is the entry point, `/make.sh`. (Make sure you have `latex`, `bibtex`, `dvips`, and `pspdf` commands available.)

    #!bash
    #!/bin/bash
    
    usage() {
        echo "Usage: $0 <BASENAME> <LATEX|BIBTEX|CLEAN>"
        exit 1
    }
    
    [ $# -ne 2 ] && usage
    BASENAME=$1
    ACTION=$2
    
    set -e
    set -x
    
    latex() {
        /usr/bin/latex --halt-on-error $1
    }
    
    make_bibtex() {
        latex $1 && \
    	bibtex $1 && \
    	latex $1 && \
    	latex $1
    }
    
    make_latex() {
        cd figs && ./make.sh && cd .. && \
        latex $1 && \
        dvips -Ppdf -G0 -ta4 $1.dvi -o && \
        ps2pdf \
    	-dCompatibilityLevel=1.4 \
    	-dPDFSETTINGS=/prepress \
    	$1.ps $1.pdf
    }
    
    make_clean() {
        rm -f \
    	$1.aux \
    	$1.bbl \
    	$1.blg \
    	$1.dvi \
    	$1.log \
    	$1.pdf \
    	$1.ps
    }
    
    case $ACTION in
        latex) make_latex $BASENAME;;
        bibtex) make_bibtex $BASENAME;;
        clean) make_clean $BASENAME;;
        *) usage;;
    esac

In `/make.sh`, I follow LaTeX->DVI->PostScript->PDF path. The main reason for the preference of this path over LaTeX->PDF is to properly process scalable EPS figures produced by XFig. (Personally, I hate to see broken figures in published articles.)

Next, here goes `/figs/make.sh` script. (Per see, gnuplot is required during execution.)

    #!bash
    #!/bin/bash
    
    set -e
    set -x
    
    get_modify_time() {
        if [ -e "$1" ]; then
    	DT=$(stat "$1" | grep ^Modify: | sed 's/^Modify: //g')
    	date -d "$DT" +%s
        else
    	echo 0
        fi
    }
    
    find -name "*.fig" | \
    while read FIG; do
        BAS=$(basename "$FIG" | sed 's/\.fig$//g')
        BAK="$BAS.fig.bak"
        EPS="$BAS.eps"
    
        # See if EPS needs to be updated.
        T_FIG=$(get_modify_time "$FIG")
        T_EPS=$(get_modify_time "$EPS")
        [ $T_FIG -gt $T_EPS ] && ./fig2eps.sh $BAS
    
        # Remove backup, if there is any.
        rm -f "$BAK"
    done
    
    find -name "*.gnu" | \
    while read GNU; do
        BAS=$(basename "$GNU" | sed 's/\.gnu$//g')
        EPS="$BAS.eps"
    
        # See if EPS needs to be updated.
        T_GNU=$(get_modify_time "$GNU")
        T_EPS=$(get_modify_time "$EPS")
        if [ $T_GNU -gt $T_EPS ]; then
    	gnuplot $GNU
        fi
    done
    
    exit 0

Nothing fancy in `/figs/make.sh`. First, we process `.fig` files; second, we process `.gnu` files.

Finally, below goes `/figs/fig2eps.sh` script. (Make `fig2dev`, `pdflatex`, `pdf2ps` commands ready. Note that `/figs/fig2eps.sh` requires `/constants.tex` for shared LaTeX variables.)

    #!bash
    #!/bin/bash
    
    set -x
    
    if [ ${#@} -ne 1 ]; then
        echo "Usage: $0 <BASENAME>"
        exit 1
    fi
    
    BASENAME="$1"
    
    cat <<EOF >$BASENAME.tex
    \documentclass{article}
    \usepackage{graphics}
    \usepackage{amsfonts}
    \usepackage{color}
    \input{../constants}
    \begin{document}
    \thispagestyle{empty}
    \begin{figure}
      \centering
      \input{${BASENAME}_fig.pdf_t}
    \end{figure}
    \end{document}
    EOF
    
    fig2dev -L pdftex $BASENAME.fig ${BASENAME}_fig.pdf && \
    fig2dev -L pstex_t -p ${BASENAME}_fig.pdf $BASENAME.fig ${BASENAME}_fig.pdf_t && \
    pdflatex $BASENAME && \
    pdf2ps $BASENAME.pdf $BASENAME.eps
    RET=$?
    
    rm -f \
        ${BASENAME}_fig.pdf \
        ${BASENAME}_fig.pdf_t \
        $BASENAME.aux \
        $BASENAME.pdf \
        $BASENAME.log \
        $BASENAME.tex
    
    exit $RET

After all these fuss, the whole project boils down to

    #!bash
    ./make.sh paper bibtex
    ./make.sh paper latex

and you are ready to go.

Scripts need a little bit more cleaning and they are probably not the most correct ones. Anyway, they served well until now, and I hope they would for you as well.
