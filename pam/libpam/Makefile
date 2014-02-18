CFLAGS +=  -Wall
all: /lib/security/pam_latch.so

clean:
	$(RM) /lib/security/pam_latch.so *.o
	
/lib/security/pam_latch.so: pam_latch.c ../latch.h
	$(CC) $(CFLAGS) -fPIC -shared -Xlinker -x -o $@ ../latch.c $< -lcurl -lcrypto -lpam
