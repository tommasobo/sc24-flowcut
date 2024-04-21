#include <iostream>
#include <fstream>
#include <iomanip>
#include <ctime>

#define TAG 0xDEADBEEF
#define CONTROL_TAG 0x01, 0x00, 0x00, 0x30
#define CONTROL_TAG_FULL 0x30000001
#define CONTROL_TAG_FULL_ALTERNATIVE 0x30000002
#define ACK_TAG 0xAC, 0xAC, 0xAC, 0xAC
#define MESSAGE_TO_SEND 'A'
#define OTHER_MESSAGE 'B'
#define ACK_MSG 'K'
#define ACK_SIZE_BYTE 4
#define SMALL_MESSAGE_SIZE 8
#define HEADER_SIZE 45
#define TAG_INDEX_START 29
#define PKT_SIZE 256
#define SAMPLING_RATE_PORT_OCCUPANCY 10000

#define PATH_INPUT_FROM_EMBER "../../../../../../plotting/raw_input"


#define MAX_FLOWCUT_SIZE 16000