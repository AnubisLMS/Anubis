####################################
# CS:APP Bomb Lab
# Makefile that builds a binary bomb
####################################

#
# The following variables determine how the bomb is built.  The
# default values shown here build a generic bomb. The makebomb.pl
# script overrides these defaults by defining environment variables of
# the same name, and then calling Make with the -e option. You can
# change these variables manually here to build different kinds of
# bombs.
#


# The CFLAGS variable sets the compiler flags to control things such
# as the optimization level (-O) and whether the binary should be 32
# bit (-m32) or 64 bit (-m64). Selecting the optimization level is a
# tradeoff between generating clean code and optimizing away things we
# want to test the students on. For example, newer versions of gcc
# such as gcc 3.4.2 do aggressive optimization at the -O2 level such
# as inlining functions and replacing tail recursion with iteration,
# while older versions generate somewhat ugly code at less than -O2.
#
CFLAGS = -Wall -O1 -m32 

# Unique name, across all terms, for this instance of the assignment
LABID = f12

#
# Default result server name and port (not needed for non-notifying bombs)
# 
SERVERNAME = $(shell echo "result.${DOMAIN}")
SERVERPORT = 80

#
# If -DNOTIFY, then send an autoresult to the server
# The default is to not notify (-DNONOTIFY). This variable
# determines whether the bomb is compiled with notifying code
# compiled in.
#
BOMBFLAGS = -DNONOTIFY 
#BOMBFLAGS = -DNOTIFY

# 
# If "BOMBLFAGS == -DNOTIFY" then set "NOTIFYFLAG = -n".
# The -s flag tells the makephases.pl script to build
# a phases.c file for a notifying bomb.
#
NOTIFYFLAG =
#NOTIFYFLAG = -n

#
# A BOMBID of zero denotes a generic bomb. A nonzero BOMBID denotes
# a custom bomb. Generic bombs are not allowed to NOTIFY. Custom bombs
# can NOTIFY or not. The default is to build a generic bomb.
#
BOMBID = 0
#BOMBID = 1

#
# IF BOMPHASES is not defined, then the makephases.pl script chooses 
# a random variant for each phase. Otherwise, use -p to indicate
# the variant you want for each phase. The default is to use variant 'a'
# for all six phases. 
#
BOMBPHASES = -p aaaaaa

####################################### 
# No need to change anything below here
#######################################
# Default userid.
USERID = bovik

# Default password.
USERPWD = gunpowder

# Default labname
LAB = bomblab

CC = gcc

all: 
	@echo "Please call make with an explicit rule"

# Run a regression test that makes and tests 100 random bombs
regression-test:
	./rtest.pl -n 100 >& rtest.log

# Generate the solution
solution.txt: bomb-solve
	./bomb-solve > solution.txt

# Check the bomb for correctness
check-bomb: 
	./bomb-solve > solution.txt
	./bomb < solution.txt	

# Build the bomb
bomb: bomb.o phases.o support.o driverlib.o 
	$(CC) $(CFLAGS) -o bomb bomb.o phases.o support.o driverlib.o

driverlib.o: driverlib.c driverlib.h
	$(CC) $(CFLAGS) -DSERVER_NAME=\"$(SERVERNAME)\" -DSERVER_PORT=$(SERVERPORT) -DLABID=\"$(LABID)\" -c driverlib.c

bomb.o: bomb.c support.h phases.h
	$(CC) $(CFLAGS) -c -ggdb bomb.c

phases.o: phases.c phases.h
	$(CC) $(CFLAGS) -DPROBLEM -c phases.c

# Rule that makebomb.pl uses to build a quiet (non-notifying)
# version of the current bomb. Makebomb.pl sets the appropriate 
# environment variables. 
bomb-quiet: bomb.o support.o phases.o 
	$(CC) $(CFLAGS) -o bomb-quiet bomb.o phases.o support.o 

# This bomb prints its solution to the stdout
bomb-solve: bomb-solve.o support.o phases-solve.o driverlib.o
	$(CC) $(CFLAGS) -o bomb-solve bomb-solve.o phases-solve.o support.o driverlib.o

bomb-solve.o: bomb-solve.c support.h phases.h 
	$(CC) $(CFLAGS) -c bomb-solve.c 

phases-solve.o: phases.c phases.h
	$(CC) $(CFLAGS) -DSOLUTION -c -o phases-solve.o phases.c

# This file provides various support routines for the bomb
# BOMBFLAGS is either "-DNOTIFY" (compile with notification enabled) 
# or "-DNONOTIFY" (compile with notification disabled)
support.o: support.c support.h config.h
	$(CC) $(BOMBFLAGS) $(CFLAGS) -c support.c


# Generate a phases.c file
phases.c: phases/*.c support.h
	./makephases.pl $(NOTIFYFLAG) $(BOMBPHASES) -d phases -i $(BOMBID) -u $(USERID) -w $(USERPWD) > phases.c

# Use this when you want to recompile with existing phases.c
clean:
	-rm -f *.o bomb bomb-quiet bomb-solve solution.txt *~

# Use this when you want to create a new phases.c file
cleanall:
	-rm -f *.o phases.c phases.s bomb bomb-quiet bomb-solve solution.txt *~



