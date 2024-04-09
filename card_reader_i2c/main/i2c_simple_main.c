/* i2c - Simple example

   Simple I2C example that shows how to initialize I2C
   as well as reading and writing from and to registers for a sensor connected over I2C.

   The sensor used in this example is a MPU9250 inertial measurement unit.

   For other examples please check:
   https://github.com/espressif/esp-idf/tree/master/examples

   See README.md file to get detailed usage of this example.

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include "esp_log.h"
#include "driver/i2c.h"
#include "sdkconfig.h"

static const char *TAG = "i2c-slave";

#define DATA_LENGTH                         512     /*!< Data buffer length of test buffer */
#define RW_TEST_LENGTH                      128     /*!< Data length for r/w test, [0,DATA_LENGTH] */
#define DELAY_TIME_BETWEEN_ITEMS_MS         20      /*!< delay time between different test items */

#define I2C_SLAVE_NUM I2C_NUM_0
#define I2C_SLAVE_SDA_IO 4
#define I2C_SLAVE_SCL_IO 5
#define I2C_SLAVE_TX_BUF_LEN 256                    //(2 * DATA_LENGTH)
#define I2C_SLAVE_RX_BUF_LEN 256                    //(2 * DATA_LENGTH)

#define ESP_SLAVE_ADDR 0x04

// Initialize buffers
uint8_t inBuff[256];
uint16_t inBuffLen = 0;
uint8_t outBuff[256];
uint16_t outBuffLen = 0;

/**
 * @brief i2c master initialization
 */
static esp_err_t i2c_slave_init() {
  i2c_port_t i2c_slave_port = I2C_SLAVE_NUM;
  i2c_config_t conf_slave;
  conf_slave.sda_io_num = I2C_SLAVE_SDA_IO;
  conf_slave.sda_pullup_en = GPIO_PULLUP_ENABLE;
  conf_slave.scl_io_num = I2C_SLAVE_SCL_IO;
  conf_slave.scl_pullup_en = GPIO_PULLUP_ENABLE;
  conf_slave.mode = I2C_MODE_SLAVE;
  conf_slave.slave.addr_10bit_en = 0;
  conf_slave.slave.slave_addr = ESP_SLAVE_ADDR;
  i2c_param_config(i2c_slave_port, &conf_slave);
  return i2c_driver_install(i2c_slave_port, conf_slave.mode,
                            I2C_SLAVE_RX_BUF_LEN, I2C_SLAVE_TX_BUF_LEN, 0);
}

/**
 * @brief test function to show buffer
 */
static void disp_buf(uint8_t *buf, int len){
    int i;
    for (i = 0; i < len; i++) {
        printf("%02x ", buf[i]);
        if ((i + 1) % 16 == 0) {
            printf("\n");
        }
    }
    printf("\n");
}

static void get_data(){
    size_t size = i2c_slave_read_buffer(I2C_SLAVE_NUM, inBuff, 1, 1000 / portTICK_RATE_MS);
}

void app_main(void)
{
    ESP_LOGI(TAG, "SLAVE--------------------------------");
    ESP_ERROR_CHECK(i2c_slave_init());

    xTaskCreate(get_data, "get_data", 1024 * 2, (void *)1, 10, NULL);
}
