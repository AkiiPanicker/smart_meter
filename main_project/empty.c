/*
 * Copyright (c) 2021, Texas Instruments Incorporated
 * All rights reserved.
 * 
 * Smart Meter Tamper Detection Display System - FINAL VERSION
 */

#include "ti_msp_dl_config.h"
#include <stdbool.h>

/* ============== TIMING CONSTANTS ============== */
#define DELAY (3000)  // 3 seconds delay between updates

/* ============== DISPLAY GPIO ============== */
#define DC_LOW()   DL_GPIO_clearPins(EXTRA_DC_PORT, EXTRA_DC_PIN)
#define DC_HIGH()  DL_GPIO_setPins(EXTRA_DC_PORT, EXTRA_DC_PIN)
#define RST_LOW()  DL_GPIO_clearPins(EXTRA_RST_PORT, EXTRA_RST_PIN)
#define RST_HIGH() DL_GPIO_setPins(EXTRA_RST_PORT, EXTRA_RST_PIN)

/* ============== DISPLAY COLORS (BGR565) ============== */
#define BLACK   0x0000
#define WHITE   0xFFFF
#define BG_RED_LIGHT    0x52DF
#define BG_GREEN_LIGHT  0xDFE5
#define TEXT_BLACK      0x0000
#define TEXT_WHITE      0xFFFF

/* ============== RANDOM NUMBER GENERATOR ============== */
uint32_t seed = 12345;

uint16_t random_range(uint16_t min, uint16_t max)
{
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    return min + (seed % (max - min + 1));
}

/* ============== STRING CONVERSION ============== */
void int_to_string(uint16_t num, char* str)
{
    int i = 0;
    if (num == 0) {
        str[0] = '0';
        str[1] = '\0';
        return;
    }
    
    while (num > 0) {
        str[i++] = (num % 10) + '0';
        num /= 10;
    }
    str[i] = '\0';
    
    int start = 0, end = i - 1;
    while (start < end) {
        char temp = str[start];
        str[start] = str[end];
        str[end] = temp;
        start++;
        end--;
    }
}

/* ============== TIME MANAGEMENT ============== */
typedef struct {
    uint8_t day;
    uint8_t month;
    uint16_t year;
    uint8_t hour;
    uint8_t minute;
    uint8_t second;
} DateTime;

void datetime_add_minutes(DateTime* dt, uint8_t minutes)
{
    dt->minute += minutes;
    if (dt->minute >= 60) {
        dt->hour += dt->minute / 60;
        dt->minute = dt->minute % 60;
        if (dt->hour >= 24) {
            dt->day += dt->hour / 24;
            dt->hour = dt->hour % 24;
        }
    }
}

/* ============== UART FUNCTIONS ============== */
void uart_send_char(char c)
{
    while(DL_UART_isBusy(UART_0_INST));
    DL_UART_Main_transmitData(UART_0_INST, c);
}

void uart_send_string(const char *str)
{
    while(*str)
    {
        uart_send_char(*str++);
    }
}

void send_sensor_data(bool tampered, uint16_t voltage, uint16_t current, uint16_t temp, uint16_t light, uint16_t mag)
{
    char buffer[16];
    
    uart_send_string("{\"voltage\":");
    int_to_string(voltage, buffer);
    uart_send_string(buffer);
    
    uart_send_string(",\"current\":");
    int_to_string(current, buffer);
    uart_send_string(buffer);
    
    uart_send_string(",\"temperature\":");
    int_to_string(temp, buffer);
    uart_send_string(buffer);
    
    uart_send_string(",\"lightIntensity\":");
    int_to_string(light, buffer);
    uart_send_string(buffer);
    
    uart_send_string(",\"magneticField\":");
    int_to_string(mag, buffer);
    uart_send_string(buffer);
    
    uart_send_string(",\"tamperFlag\":");
    uart_send_char(tampered ? '1' : '0');
    uart_send_string("}\r\n");
}

/* ============== DELAY FUNCTIONS ============== */
void delay_ms(uint32_t ms)
{
    while (ms--) delay_cycles(32000);
}

/* ============== SPI FUNCTIONS ============== */
static inline void spi_tx(uint8_t b)
{
    DL_SPI_fillTXFIFO8(SPI_0_INST, &b, 1);
    while (DL_SPI_isBusy(SPI_0_INST));
}

/* ============== LCD PRIMITIVES ============== */
static void lcd_cmd(uint8_t c)
{
    DC_LOW();
    spi_tx(c);
}

static void lcd_data(uint8_t d)
{
    DC_HIGH();
    spi_tx(d);
}

static void lcd_reset(void)
{
    RST_LOW();
    delay_ms(20);
    RST_HIGH();
    delay_ms(150);
}

static void ili9341_init(void)
{
    lcd_reset();
    lcd_cmd(0x11);
    delay_ms(120);
    lcd_cmd(0x3A);
    lcd_data(0x55);
    lcd_cmd(0x36);
    lcd_data(0xC8);
    lcd_cmd(0x29);
    delay_ms(20);
}

static void lcd_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1)
{
    lcd_cmd(0x2A);
    lcd_data(x0 >> 8); lcd_data(x0 & 0xFF);
    lcd_data(x1 >> 8); lcd_data(x1 & 0xFF);
    lcd_cmd(0x2B);
    lcd_data(y0 >> 8); lcd_data(y0 & 0xFF);
    lcd_data(y1 >> 8); lcd_data(y1 & 0xFF);
    lcd_cmd(0x2C);
}

static void lcd_draw_pixel(uint16_t x, uint16_t y, uint16_t color)
{
    if (x >= 240 || y >= 320) return;
    lcd_set_window(x, y, x, y);
    DC_HIGH();
    spi_tx(color >> 8);
    spi_tx(color & 0xFF);
}

static void lcd_fill(uint16_t color)
{
    lcd_set_window(0, 0, 239, 319);
    DC_HIGH();
    for (uint32_t i = 0; i < 76800; i++) {
        spi_tx(color >> 8);
        spi_tx(color & 0xFF);
    }
}

static void lcd_fill_rect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color)
{
    lcd_set_window(x, y, x+w-1, y+h-1);
    DC_HIGH();
    for (uint32_t i = 0; i < (uint32_t)w * h; i++) {
        spi_tx(color >> 8);
        spi_tx(color & 0xFF);
    }
}

/* ============== 5x7 FONT (EXTENDED WITH l AND x) ============== */
static const uint8_t font5x7[][5] = {
    {0x00, 0x00, 0x00, 0x00, 0x00}, // 0: space
    {0x3E, 0x51, 0x49, 0x45, 0x3E}, // 1: 0
    {0x00, 0x42, 0x7F, 0x40, 0x00}, // 2: 1
    {0x42, 0x61, 0x51, 0x49, 0x46}, // 3: 2
    {0x21, 0x41, 0x45, 0x4B, 0x31}, // 4: 3
    {0x18, 0x14, 0x12, 0x7F, 0x10}, // 5: 4
    {0x27, 0x45, 0x45, 0x45, 0x39}, // 6: 5
    {0x3C, 0x4A, 0x49, 0x49, 0x30}, // 7: 6
    {0x01, 0x71, 0x09, 0x05, 0x03}, // 8: 7
    {0x36, 0x49, 0x49, 0x49, 0x36}, // 9: 8
    {0x06, 0x49, 0x49, 0x29, 0x1E}, // 10: 9
    {0x00, 0x36, 0x36, 0x00, 0x00}, // 11: :
    {0x7C, 0x12, 0x11, 0x12, 0x7C}, // 12: A
    {0x7F, 0x49, 0x49, 0x49, 0x36}, // 13: C
    {0x7F, 0x41, 0x41, 0x22, 0x1C}, // 14: D
    {0x7F, 0x49, 0x49, 0x49, 0x41}, // 15: E
    {0x7F, 0x09, 0x09, 0x09, 0x01}, // 16: F
    {0x3E, 0x41, 0x49, 0x49, 0x7A}, // 17: G
    {0x7F, 0x08, 0x08, 0x08, 0x7F}, // 18: H
    {0x00, 0x41, 0x7F, 0x41, 0x00}, // 19: I
    {0x7F, 0x40, 0x40, 0x40, 0x40}, // 20: L
    {0x7F, 0x02, 0x0C, 0x02, 0x7F}, // 21: M
    {0x7F, 0x04, 0x08, 0x10, 0x7F}, // 22: N
    {0x3E, 0x41, 0x41, 0x41, 0x3E}, // 23: O
    {0x7F, 0x09, 0x09, 0x09, 0x06}, // 24: P
    {0x7F, 0x09, 0x19, 0x29, 0x46}, // 25: R
    {0x46, 0x49, 0x49, 0x49, 0x31}, // 26: S
    {0x01, 0x01, 0x7F, 0x01, 0x01}, // 27: T
    {0x3F, 0x40, 0x40, 0x40, 0x3F}, // 28: V
    {0x03, 0x04, 0x78, 0x04, 0x03}, // 29: Y
    {0x00, 0x41, 0x36, 0x08, 0x00}, // 30: /
    {0x00, 0x00, 0x7F, 0x00, 0x00}, // 31: l (lowercase L)
    {0x63, 0x14, 0x08, 0x14, 0x63}, // 32: x (lowercase x)
};

static void lcd_draw_char(uint16_t x, uint16_t y, char c, uint16_t color, uint8_t size)
{
    uint8_t idx = 0;
    
    if (c == ' ') idx = 0;
    else if (c >= '0' && c <= '9') idx = 1 + (c - '0');
    else if (c == ':') idx = 11;
    else if (c == 'A') idx = 12;
    else if (c == 'C') idx = 13;
    else if (c == 'D') idx = 14;
    else if (c == 'E') idx = 15;
    else if (c == 'F') idx = 16;
    else if (c == 'G') idx = 17;
    else if (c == 'H') idx = 18;
    else if (c == 'I') idx = 19;
    else if (c == 'L') idx = 20;
    else if (c == 'M') idx = 21;
    else if (c == 'N') idx = 22;
    else if (c == 'O') idx = 23;
    else if (c == 'P') idx = 24;
    else if (c == 'R') idx = 25;
    else if (c == 'S') idx = 26;
    else if (c == 'T') idx = 27;
    else if (c == 'V') idx = 28;
    else if (c == 'Y') idx = 29;
    else if (c == '/') idx = 30;
    else if (c == 'l') idx = 31;
    else if (c == 'x') idx = 32;
    else return;
    
    for (uint8_t i = 0; i < 5; i++) {
        uint8_t line = font5x7[idx][i];
        for (uint8_t j = 0; j < 8; j++) {
            if (line & 0x01) {
                for (uint8_t sx = 0; sx < size; sx++) {
                    for (uint8_t sy = 0; sy < size; sy++) {
                        lcd_draw_pixel(x + i*size + sx, y + j*size + sy, color);
                    }
                }
            }
            line >>= 1;
        }
    }
}

static void lcd_draw_string(uint16_t x, uint16_t y, const char* str, uint16_t color, uint8_t size)
{
    uint16_t offset = 0;
    while (*str) {
        lcd_draw_char(x + offset, y, *str, color, size);
        offset += 6 * size;
        str++;
    }
}

static void lcd_draw_number(uint16_t x, uint16_t y, uint16_t num, uint16_t color, uint8_t size)
{
    char buffer[6];
    int_to_string(num, buffer);
    lcd_draw_string(x, y, buffer, color, size);
}

/* ============== DRAW HAPPY STATUS ICON ============== */
static void draw_status_icon(uint16_t x, uint16_t y, bool is_ok)
{
    lcd_fill_rect(x, y, 70, 3, TEXT_BLACK);
    lcd_fill_rect(x, y+87, 70, 3, TEXT_BLACK);
    lcd_fill_rect(x, y, 3, 90, TEXT_BLACK);
    lcd_fill_rect(x+67, y, 3, 90, TEXT_BLACK);
    
    if (is_ok) {
        lcd_fill_rect(x+15, y+15, 40, 3, TEXT_BLACK);
        lcd_fill_rect(x+15, y+62, 40, 3, TEXT_BLACK);
        lcd_fill_rect(x+15, y+15, 3, 50, TEXT_BLACK);
        lcd_fill_rect(x+52, y+15, 3, 50, TEXT_BLACK);
        
        lcd_fill_rect(x+25, y+28, 6, 6, TEXT_BLACK);
        lcd_fill_rect(x+42, y+28, 6, 6, TEXT_BLACK);
        
        lcd_fill_rect(x+23, y+48, 26, 3, TEXT_BLACK);
        lcd_fill_rect(x+23, y+45, 3, 6, TEXT_BLACK);
        lcd_fill_rect(x+46, y+45, 3, 6, TEXT_BLACK);
        
    } else {
        lcd_fill_rect(x+30, y+15, 10, 45, TEXT_BLACK);
        lcd_fill_rect(x+30, y+65, 10, 10, TEXT_BLACK);
    }
}

/* ============== DISPLAY SCREEN ============== */
static void display_meter_screen(uint8_t is_tamper, uint16_t voltage, uint16_t curr, uint16_t temp, 
                                  uint16_t light, uint16_t mag, uint16_t events, DateTime* last_dt)
{
    uint16_t bg_color = is_tamper ? BG_RED_LIGHT : BG_GREEN_LIGHT;
    const char* status_text = is_tamper ? "TAMPERING" : "NORMAL";
    
    lcd_fill(bg_color);
    
    lcd_draw_string(40, 8, "LATEST TAMPER", TEXT_BLACK, 2);
    
    char date_str[11];
    date_str[0] = (last_dt->day / 10) + '0';
    date_str[1] = (last_dt->day % 10) + '0';
    date_str[2] = '/';
    date_str[3] = (last_dt->month / 10) + '0';
    date_str[4] = (last_dt->month % 10) + '0';
    date_str[5] = '/';
    date_str[6] = ((last_dt->year / 1000) % 10) + '0';
    date_str[7] = ((last_dt->year / 100) % 10) + '0';
    date_str[8] = ((last_dt->year / 10) % 10) + '0';
    date_str[9] = (last_dt->year % 10) + '0';
    date_str[10] = '\0';
    lcd_draw_string(60, 28, date_str, TEXT_BLACK, 2);
    
    char time_str[9];
    time_str[0] = (last_dt->hour / 10) + '0';
    time_str[1] = (last_dt->hour % 10) + '0';
    time_str[2] = ':';
    time_str[3] = (last_dt->minute / 10) + '0';
    time_str[4] = (last_dt->minute % 10) + '0';
    time_str[5] = ':';
    time_str[6] = (last_dt->second / 10) + '0';
    time_str[7] = (last_dt->second % 10) + '0';
    time_str[8] = '\0';
    lcd_draw_string(72, 46, time_str, TEXT_BLACK, 2);
    
    lcd_fill_rect(10, 64, 220, 2, TEXT_BLACK);
    
    // Voltage
    lcd_draw_string(10, 75, "V :  ", TEXT_BLACK, 2);
    lcd_draw_number(52, 75, voltage, TEXT_BLACK, 2);
    lcd_draw_string(88, 75, " V", TEXT_BLACK, 2);
    
    // Current
    lcd_draw_string(10, 105, "I :  ", TEXT_BLACK, 2);
    lcd_draw_number(52, 105, curr, TEXT_BLACK, 2);
    lcd_draw_string(88, 105, " A", TEXT_BLACK, 2);
    
    // Temperature
    lcd_draw_string(10, 135, "T :  ", TEXT_BLACK, 2);
    lcd_draw_number(52, 135, temp, TEXT_BLACK, 2);
    lcd_draw_string(88, 135, " C", TEXT_BLACK, 2);
    
    // Light with proper lx
    lcd_draw_string(10, 165, "L :  ", TEXT_BLACK, 2);
    lcd_draw_number(52, 165, light, TEXT_BLACK, 2);
    lcd_draw_string(88, 165, " lx", TEXT_BLACK, 2);
    
    // Magnetic
    lcd_draw_string(10, 195, "M :  ", TEXT_BLACK, 2);
    lcd_draw_number(52, 195, mag, TEXT_BLACK, 2);
    lcd_draw_string(88, 195, " T", TEXT_BLACK, 2);
    
    // Events
    lcd_draw_string(10, 225, "E :  ", TEXT_BLACK, 2);
    lcd_draw_number(52, 225, events, TEXT_BLACK, 2);
    
    draw_status_icon(160, 110, !is_tamper);
    
    lcd_fill_rect(0, 270, 240, 50, BLACK);
    lcd_draw_string(is_tamper ? 12 : 48, 283, status_text, TEXT_WHITE, 4);
}

/* ============== MAIN ============== */
int main(void)
{
    SYSCFG_DL_init();

    DC_LOW();
    RST_HIGH();
    ili9341_init();

    uint16_t hist_voltage = 237;
    uint16_t hist_current = 95;
    uint16_t hist_temp = 48;
    uint16_t hist_light = 189;
    uint16_t hist_mag = 112;
    uint16_t hist_events = 1;
    
    DateTime last_tamper_dt = {10, 1, 2026, 1, 5, 0};
    
    uint16_t loop_counter = 0;

    uart_send_string("Smart Meter System initialized\r\n");
    display_meter_screen(0, hist_voltage, hist_current, hist_temp, hist_light, hist_mag, hist_events, &last_tamper_dt);

    while(1)
    {
        loop_counter++;
        bool is_tamper = (loop_counter % 4 == 0);

        uint16_t voltage, current, temp, light, mag;
        
        voltage = random_range(230, 240);
        
        if (is_tamper) {
            current = random_range(50, 150);
            temp = random_range(40, 60);
            light = random_range(150, 250);
            mag = random_range(80, 150);
            
            hist_voltage = voltage;
            hist_current = current;
            hist_temp = temp;
            hist_light = light;
            hist_mag = mag;
            hist_events++;
            
            datetime_add_minutes(&last_tamper_dt, 5);
            
        } else {
            current = random_range(1, 15);
            temp = random_range(20, 35);
            light = random_range(0, 30);
            mag = random_range(0, 10);
        }
        
        send_sensor_data(is_tamper, voltage, current, temp, light, mag);
        
        if (is_tamper) {
            display_meter_screen(is_tamper, voltage, current, temp, light, mag, hist_events, &last_tamper_dt);
        } else {
            display_meter_screen(is_tamper, hist_voltage, hist_current, hist_temp, hist_light, hist_mag, hist_events, &last_tamper_dt);
        }

        delay_ms(DELAY);  // 3 second delay
    }
}
