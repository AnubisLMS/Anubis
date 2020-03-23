/* 
 * phase5a.c - Just to be hairy, this traverses a loop of pointers and 
 * counts its length.  The input determines where in the loop we begin. 
 * Just to make sure the user isn't guessing, we make them input the sum of
 * the pointers encountered along the path, too.
 */
void phase_5(char *input)
{
#if defined(PROBLEM)
    static int array[] = {
      10,
      2,
      14,
      7,
      8,
      12,
      15,
      11,
      0,
      4,
      1,
      13,
      3,
      9,
      6,
      5
    };

    int count, sum;
    int start;
    int p, result;
    int numScanned;

    numScanned = sscanf(input, "%d %d", &p, &result);
    
    if (numScanned < 2)
      explode_bomb();

    p = p & 0x0f;
    start = p; /* debug */

    count = 0;
    sum = 0;
    while(p != 15) {
	count++;
	p = array[p];
	sum += p;
    }

    if ((count != COUNT_VALUE_SET) || (sum != result))
	explode_bomb();
#elif defined(SOLUTION)
    switch (COUNT_VALUE_GET) {
    case 1: printf("6 15"); break;
    case 2: printf("14 21"); break;
    case 3: printf("2 35"); break;
    case 4: printf("1 37"); break;
    case 5: printf("10 38"); break;
    case 6: printf("0 48"); break;
    case 7: printf("8 48"); break;
    case 8: printf("4 56"); break;
    case 9: printf("9 60"); break;
    case 10: printf("13 69"); break;
    case 11: printf("11 82"); break;
    case 12: printf("7 93"); break;
    case 13: printf("3 100"); break;
    case 14: printf("12 103"); break;
    case 15: printf("5 115"); break;
    default:
	printf("ERROR: bad count value in phase5a\n");
	exit(8);
    }
    printf("\n");
#else
    invalid_phase("5a");
#endif
}

