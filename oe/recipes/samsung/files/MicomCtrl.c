
#include <stdio.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>
#include <sys/fcntl.h>

int main(int argc, char* argv[]) {
	int fd, i;
	unsigned char buf[9];
	struct termios newtio;

	fd = open("/dev/ttyS0", O_RDWR | O_NOCTTY);
	if (fd < 0) {
		printf("Error open /dev/ttyS0\n");
		return -1;
	}

	bzero((void *)&newtio, sizeof(newtio));
	newtio.c_cflag = B9600 | CS8 | CLOCAL | CREAD;
	newtio.c_iflag = IGNPAR;
	newtio.c_oflag = OPOST;
	newtio.c_lflag = 0;
	newtio.c_cc[VTIME] = 0;
	newtio.c_cc[VMIN] = 1;
	tcflush(fd, TCIOFLUSH);
	tcsetattr(fd, TCSANOW, &newtio);

	memset(buf, 0, 9);
	buf[0] = 0xff;
	buf[1] = 0xff;

	if (argc > 6)
		argc = 6;

	for (i = 0; i < argc - 1;  i++) {
		buf[i + 2] = atoi(argv[i + 1]);
		buf[8] += buf[i + 2];
	}

	write(fd, buf, 9);
	usleep(10000);
	close(fd);

	return 0;
}

