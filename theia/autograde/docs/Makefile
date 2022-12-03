# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
PYTHON       ?= python
SPHINXOPTS    =
SPHINXBUILD   = -msphinx
SPHINXPROJ    = anubis
SOURCEDIR     = .
BUILDDIR      = .

# Put it first so that "make" without argument is like "make help".
help:
	@$(PYTHON) $(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(PYTHON) $(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# https://sphinx-gallery.github.io/stable/advanced.html#cleaning-the-gallery-files
clean:
	rm -rf $(BUILDDIR)/html $(BUILDDIR)/doctrees
	rm -rf assignment.rst
	rm -rf modules.rst
	rm -rf pipeline.rst
	rm -rf utils.rst

# https://sphinx-gallery.github.io/stable/advanced.html#build-the-gallery-without-running-any-examples
html-noplot:
	$(PYTHON) $(SPHINXBUILD) -D plot_gallery=0 -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."
