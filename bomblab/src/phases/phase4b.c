/* 
 * phase4b.c - A recursive binary search function to sort out.  The
 * search is over the indexes [0..14] of a binary search tree, where
 * root=7, root->left=3, root->right=11, and so on.  The user must
 * predict the path through the tree (expressed as a 3-bit int where
 * 0=left, 1=right, read lsb to msb) of the indexes that will be
 * visited during the search for a particular target value, and must
 * input both the path and the target value.
 */
int func4(int val, int low, int high)
{
    int mid;

    mid = low + (high - low) / 2;

    if (mid > val)
	return func4(val, low, mid-1) << 1;
    else if (mid < val)
	return (func4(val, mid+1, high) << 1) + 1;
    else
	return 0;
}


void phase_4(char *input) {
#if defined(PROBLEM)
    int user_val, user_path, result, target_path, numScanned;

    numScanned = sscanf(input, "%d %d", &user_val, &user_path);
    if ((numScanned != 2) || user_val < 0 || user_val > 14) {
	explode_bomb();
    }

    target_path = RANDOM_PATH_SET; 
    result = func4(user_val, 0, 14);

    if (result != target_path || user_path != target_path) {
	explode_bomb();
    }
#elif defined(SOLUTION)
    int i;
    int target_path = RANDOM_PATH_GET;
    
    for (i=0; i<15; i++) { 
	if (target_path == func4(i, 0, 14))
	    break;
    }
	printf("%d %d %s\n", i, target_path, SECRET_PHRASE);
#else
    invalid_phase("4a");
#endif
}

