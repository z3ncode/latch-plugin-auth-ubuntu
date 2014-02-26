#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


int main( void )
{
   execl("/usr/lib/latch/system/latchPluginGUI.py", "latchPluginGUI.py", NULL);

   return 0;
}
