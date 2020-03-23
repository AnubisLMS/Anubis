/* 
 * phase3c.c - A long switch statement that the compiler should implement
 * with a jump table. The user has to enter both an index into the table
 * and the character stored at that position in the table as well
 * as a number to be compared. 
 */
void phase_3(char *input) 
{
#if defined(PROBLEM)
    int index, num, numScanned = 0;
    char x, letter;
  
    numScanned = sscanf(input, "%d %c %d", &index, &letter, &num);
  
    if (numScanned < 3) {
	explode_bomb();
    }

    switch(index) {
    case 0:
	x = 'LETTER';
	if(num != POSITIVE) {
	    explode_bomb();
	}
	break;
    case 1:
	x = 'LETTER';
	if(num != POSITIVE) {
	    explode_bomb();
	}
	break;
    case 2:
	x = 'LETTER';
	if(num != POSITIVE) {
	    explode_bomb();
	}
	break;
    case 3:
	x = 'LETTER';
	if(num != POSITIVE) {
	    explode_bomb();
	}
	break;
    case 4:
	x = 'LETTER';
	if(num != POSITIVE) {
	    explode_bomb();
	}
	break;
    case 5:
	x = 'LETTER_SET';
	if(num != POSITIVE_SET) {
	    explode_bomb();
	}
	break;
    case 6:
	x = 'LETTER';
	if(num != POSITIVE) {
	    explode_bomb();
	}
	break;
    case 7:
	x = 'LETTER';
	if(num != POSITIVE) {
	    explode_bomb();
	}
	break;
    default:
	x = 'LETTER'; /* keep gcc happy */
	explode_bomb();
    }
  
    if (x != letter) {
	explode_bomb();
    }
#elif defined(SOLUTION)
    printf("5 LETTER_GET POSITIVE_GET\n");
#else
    invalid_phase("3c");
#endif
}

