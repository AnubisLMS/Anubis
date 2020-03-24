/* 
 * phase3b.c - A long switch statement that the compiler should
 * implement with a jump table. The user must enter both an index 
 * into the table and the sum accumulated by falling through the rest 
 * of the table 
 */

void phase_3(char *input)
{
#if defined(PROBLEM)
    int index, sum, x = 0;
    int numScanned = 0;

    numScanned = sscanf(input, "%d %d", &index, &sum);

    if (numScanned < 2)
	explode_bomb();

    switch(index) {
    case 0:
	x = x + POSITIVE;
    case 1:
	x = x - POSITIVE;
    case 2:
	x = x + POSITIVE;
    case 3:
	x = x - POSITIVE_SET;
    case 4:
	x = x + POSITIVE_GET;
    case 5:
	x = x - POSITIVE_GET;
    case 6:
	x = x + POSITIVE_GET;
    case 7:
	x = x - POSITIVE_GET;
	break;
    default:
	explode_bomb();
    }

    if ((index > 5) || (x != sum))
	explode_bomb();
#elif defined(SOLUTION)
    printf("3 -POSITIVE_GET\n");
#else
    invalid_phase("3b");
#endif
}
