#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


int main(int argc, char **argv)
{
	if(argc == 2){
		execl("/usr/lib/latch/system/pair.py", "pair.py", argv[1], NULL);
	}else if(argc == 4 && strncmp("-f", argv[2], 2) == 0){
		execl("/usr/lib/latch/system/pair.py", "pair.py", argv[1], "-f", argv[3], NULL);
	}else{
        	printf("use 'pairSYS <TOKEN> [-f latch.conf]'\n");
	}

	return 0;
}
