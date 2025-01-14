#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdint.h>

#define SOCKET_PATH "/tmp/sensor_socket"
#define MAX_LOCATION 16

// Must match Python struct exactly
#pragma pack(1)
struct sensor_reading {
    uint16_t sensor_id;
    float temperature;
    float humidity;
    int32_t timestamp;
    char location[MAX_LOCATION];
};
#pragma pack()

void print_reading(struct sensor_reading *reading) {
    printf("Sensor Reading:\n");
    printf("  Sensor ID: %d\n", reading->sensor_id);
    printf("  Temperature: %.2f°C\n", reading->temperature);
    printf("  Humidity: %.2f%%\n", reading->humidity);
    printf("  Timestamp: %d\n", reading->timestamp);
    printf("  Location: %s\n", reading->location);
    printf("\n");
}

int main() {
    int server_fd, client_fd;
    struct sockaddr_un addr;
    struct sensor_reading reading;

    // Remove existing socket if present
    unlink(SOCKET_PATH);

    // Create socket
    if ((server_fd = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
        perror("socket error");
        exit(1);
    }

    // Bind socket
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path)-1);

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        perror("bind error");
        exit(1);
    }

    // Listen for connections
    if (listen(server_fd, 5) == -1) {
        perror("listen error");
        exit(1);
    }

    printf("C program listening on %s...\n", SOCKET_PATH);

    while (1) {
        if ((client_fd = accept(server_fd, NULL, NULL)) == -1) {
            perror("accept error");
            continue;
        }

        // Read sensor data
        ssize_t bytes_read = read(client_fd, &reading, sizeof(reading));
        if (bytes_read == sizeof(reading)) {
            print_reading(&reading);
        } else {
            printf("Error: received incomplete data (%zd bytes)\n", bytes_read);
        }

        // Send acknowledgment
        uint32_t ack = 1;
        write(client_fd, &ack, sizeof(ack));

        close(client_fd);
    }

    close(server_fd);
    unlink(SOCKET_PATH);
    return 0;
}