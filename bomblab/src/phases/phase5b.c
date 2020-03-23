/*
 * phase5b.c - This stage requires the user to enter a string of
 * six characters, where each character in the string is used as an offset
 * into the character array.  The six characters indexed by the
 * offsets must spell out a particular word.
 */
void phase_5(char *input)
{
#if defined(PROBLEM)
    static char array[] = {
	'm',
	'a',
	'd',
	'u',
	'i',
	'e',
	'r',
	's',
	'n',
	'f',
	'o',
	't',
	'v',
	'b',
	'y',
	'l'
    };

    int i, length;
    char theWord[7];

    length = string_length(input);
    if (length != 6)
	explode_bomb();
    
    for (i = 0; i < 6; i++)
	theWord[i] = array[ (input[i] & 0x0f) ];
    theWord[6] = '\0';

    /* devils, flyers, flames, bruins, sabres, oilers */
    if (strings_not_equal(theWord, "SHORT_WORD_SET") != 0)
	explode_bomb();
#elif defined(SOLUTION)
    if (!strcmp("SHORT_WORD_GET", "devils"))
	printf("25l4o7\n");
    else if (!strcmp("SHORT_WORD_GET", "flyers"))
	printf("9on567\n");
    else if (!strcmp("SHORT_WORD_GET", "flames"))
	printf("9o1057\n");
    else if (!strcmp("SHORT_WORD_GET", "bruins"))
	printf("m63487\n");
    else if (!strcmp("SHORT_WORD_GET", "sabres"))
	printf("71m657\n");
    else if (!strcmp("SHORT_WORD_GET", "oilers"))
	printf("j4o567\n");
    else {
	printf("ERROR: bad short_word in phase 5b\n");
	exit(8);
    }
#else
invalid_phase("5b");
#endif
}

