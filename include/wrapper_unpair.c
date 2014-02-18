#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


int main(int argc, char **argv)
{
	if(argc == 1){
		execl("/usr/lib/latch/unpair.py", "unpair.py", NULL);
	}else if(argc == 3 && strncmp("-f", argv[1], 2) == 0){
		execl("/usr/lib/latch/unpair.py", "unpair.py", "-f", argv[3], NULL);
	}else{
        	printf("use 'unpairSYS [-f latch.conf]'\n");
	}

	return 0;
}
