/* 
 * phase3a.c - A long switch statement that the compiler should implement
 * with a jump table. The user has to enter both an index into the table 
 * and a value stored there.
 */
void phase_3(char *input)
{
#if defined(PROBLEM)
    int index, val, x = 0;
    int numScanned = 0;

    numScanned = sscanf(input, "%d %d", &index, &val);

    if (numScanned < 2)
	explode_bomb();

    switch(index) {
    case 0:
	x = POSITIVE;
	break;
    case 1:
	x = POSITIVE;
	break;
    case 2:
	x = POSITIVE;
	break;
    case 3:
	x = POSITIVE;
	break;
    case 4:
	x = POSITIVE_SET;
	break;
    case 5:
	x = POSITIVE;
	break;
    case 6:
	x = POSITIVE;
	break;
    case 7:
	x = POSITIVE;
	break;
    default:
	explode_bomb();
    }

    if (x != val)
	explode_bomb();
#elif defined(SOLUTION)
    printf("4 POSITIVE_GET\n");
#else
    invalid_phase("3a");
#endif
}
