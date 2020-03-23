#####################################################################
# CS:APP Bomb Lab
# Main makefile 
######################################################################

# Start the bomb lab by running the main bomblab daemon, which nannies the
# request and result servers and the report deamon.
start:
	@touch log.txt
	@./bomblab.pl -q &
	@ sleep 1

# Stops the bomb lab by killing all bomblab daemons
stop:
	@killall -q -9 bomblab.pl bomblab-requestd.pl bomblab-reportd.pl \
	bomblab-resultd.pl ; true

# Cleans soft state from the directory. You can do this at any time
# without hurting anything.
clean:
	rm -f *~
	(cd src; make clean)
	(cd writeup; make clean)

#
# Cleans the entire directory tree of all soft state, as well as the
# hard state releated to a specific instance of the course, such as
# bombs and log files. 
#
# Do this whenver you need a fresh directory, for example while you're
# getting the lab set up and just testing things out for yourself, or
# at the beginning of the term when you need to reset the lab.
#
# DON'T DO THIS UNLESS YOU'RE REALLY SURE!  
#
cleanallfiles:
	rm -rf *~ scores.txt bombs/bomb* log.txt log-status.txt *.html
	(cd src; make cleanall)
	(cd writeup; make clean)


