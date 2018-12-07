#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <pthread.h>
#include <sys/mman.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <ctype.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <sys/epoll.h>
#define	_PORT		8000
#define	_BUF_SIZE	1500
#define	_LISTEN		128
#define	_IP_SIZE	16
#define	TRUE	1
#define	FALSE	0
#define	CREATE_DES	10
#define	_TIMEOUT 3
#define USER_URL 0
#define USER_HTML 1
#define PRE_URL  2
#define PRE_HTML 3
#define URL_SET 5

pthread_mutex_t alock = PTHREAD_MUTEX_INITIALIZER;
typedef struct
{
	void * (*task)(void*);
	void * arg;
}task_t;

typedef struct _client
{
    int type;
    int clientfd;
    int PORT;
    char HOST[100];
    struct _client* pNext;
}Client;

void client_delete(int );
void client_append(Client** );
void client_show();
typedef struct
{
	pthread_mutex_t pool_lock;
	pthread_mutex_t arg_lock;
	pthread_cond_t not_full;
	pthread_cond_t not_empty;
	pthread_t * threads; //(pthread_t *)malloc(max*(pthread_t))
	pthread_t Manager_tid;
	task_t * task_queue;
	int pool_min;
	int pool_max;
	int alive;
	int busy;
	int queue_front;
	int queue_rear;
	int queue_max;
	int queue_size;
	int pool_shutDown;
	int wait;
}pool_t;
Client* find_next_client(Client*,int);
Client* find_client(int );
pool_t * Pool_Create(int , int ,int);
int Pool_Add_TaskQueue(pool_t *,void*(*)(void * ),void * );
void * Pool_Def_Task(void *);
void * Pool_Mana_Task(void *);
int if_alive_thread(pthread_t);
void * server_work(void *);
int init_socket(void);
