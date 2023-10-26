

#include <stdio.h>
#include <pthread.h>

#define THREAD_COUNT 128

struct args {
    pthread_cond_t cond_var;
    pthread_mutex_t cond_lock;
};

void *
lazy_thread(void *arg __attribute__((unused))) {
    /* Block on the provided cond var */
    printf("thread!\n");
    struct args *t_args = (struct args *)arg;
    pthread_mutex_lock(&(t_args->cond_lock));
    pthread_cond_wait(&(t_args->cond_var), &(t_args->cond_lock));
    pthread_mutex_unlock(&(t_args->cond_lock));
    return NULL;
}

void *
naughty_thread(void *arg __attribute__((unused))) {
    while(1) {
        printf("thread ...\n");
    }
    return NULL;
}

int
main(int argc, char **argv) {

    pthread_t thread_arr[THREAD_COUNT] = {0};
    struct args t_args = {0};
    pthread_mutex_init(&(t_args.cond_lock), NULL);
    pthread_cond_init(&(t_args.cond_var), NULL);

    /*
     * For the purpose of the demo, thread apply all bt lists high to low
     * so we need to launch the naught thread "early" to hide it in the
     * haystack ;)
     */
    pthread_create(&(thread_arr[0]), NULL, naughty_thread, NULL);
    for (size_t i = 1; i < THREAD_COUNT; i++) {
        pthread_create(&(thread_arr[i]), NULL, lazy_thread, &t_args);
    }

    /* These threads all block forever, so we only need to block main somehow. */
    pthread_join(thread_arr[1], NULL);
}

