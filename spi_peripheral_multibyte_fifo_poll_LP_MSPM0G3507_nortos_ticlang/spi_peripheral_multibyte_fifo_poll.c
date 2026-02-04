#include "ti_msp_dl_config.h"
#include <math.h>

/* ---------------- GPIO ---------------- */
#define DC_LOW()   DL_GPIO_clearPins(EXTRA_DC_PORT, EXTRA_DC_PIN)
#define DC_HIGH()  DL_GPIO_setPins(EXTRA_DC_PORT, EXTRA_DC_PIN)
#define RST_LOW()  DL_GPIO_clearPins(EXTRA_RST_PORT, EXTRA_RST_PIN)
#define RST_HIGH() DL_GPIO_setPins(EXTRA_RST_PORT, EXTRA_RST_PIN)

/* ---------------- Colors ---------------- */
#define BLACK   0x0000
#define YELLOW  0xFFE0

/* ---------------- Display ---------------- */
#define LCD_W 176
#define LCD_H 220

/* ---------------- Delay ---------------- */
static void delay_ms(uint32_t ms)
{
    while (ms--) delay_cycles(32000);
}

/* ---------------- SPI ---------------- */
static inline void spi_tx(uint8_t b)
{
    DL_SPI_fillTXFIFO8(SPI_0_INST, &b, 1);
    while (DL_SPI_isBusy(SPI_0_INST));
}

/* ---------------- LCD Low Level ---------------- */
static void lcd_write_reg(uint16_t reg)
{
    DC_LOW();
    spi_tx(reg >> 8);
    spi_tx(reg & 0xFF);
}

static void lcd_write_data(uint16_t data)
{
    DC_HIGH();
    spi_tx(data >> 8);
    spi_tx(data & 0xFF);
}

static void lcd_write_register(uint16_t reg, uint16_t data)
{
    lcd_write_reg(reg);
    lcd_write_data(data);
}

static void lcd_reset(void)
{
    RST_LOW();
    delay_ms(50);
    RST_HIGH();
    delay_ms(150);
}

/* ---------------- ILI9225 Init ---------------- */
static void ili9225_init(void)
{
    lcd_reset();

    lcd_write_register(0x0010, 0x0000);
    lcd_write_register(0x0011, 0x0000);
    lcd_write_register(0x0012, 0x0000);
    lcd_write_register(0x0013, 0x0000);
    lcd_write_register(0x0014, 0x0000);
    delay_ms(40);

    lcd_write_register(0x0011, 0x0018);
    lcd_write_register(0x0012, 0x6121);
    lcd_write_register(0x0013, 0x006F);
    lcd_write_register(0x0014, 0x495F);
    lcd_write_register(0x0010, 0x0800);
    delay_ms(10);
    lcd_write_register(0x0011, 0x103B);
    delay_ms(50);

    lcd_write_register(0x0001, 0x011C);
    lcd_write_register(0x0002, 0x0100);
    lcd_write_register(0x0003, 0x1030);
    lcd_write_register(0x0007, 0x0000);
    lcd_write_register(0x0008, 0x0808);
    lcd_write_register(0x000B, 0x1100);
    lcd_write_register(0x000C, 0x0000);
    lcd_write_register(0x000F, 0x0D01);
    lcd_write_register(0x0020, 0x0000);
    lcd_write_register(0x0021, 0x0000);

    lcd_write_register(0x0007, 0x0012);
    delay_ms(50);
    lcd_write_register(0x0007, 0x1017);
}

/* ---------------- Window ---------------- */
static void lcd_set_window(uint16_t x0, uint16_t y0,
                           uint16_t x1, uint16_t y1)
{
    if (x1 >= LCD_W) x1 = LCD_W - 1;
    if (y1 >= LCD_H) y1 = LCD_H - 1;

    lcd_write_register(0x0036, x1);
    lcd_write_register(0x0037, x0);
    lcd_write_register(0x0038, y1);
    lcd_write_register(0x0039, y0);
    lcd_write_register(0x0020, x0);
    lcd_write_register(0x0021, y0);
    lcd_write_reg(0x0022);
}

/* ---------------- Fill Rect ---------------- */
static void lcd_fill_rect(uint16_t x0, uint16_t y0,
                          uint16_t x1, uint16_t y1,
                          uint16_t color)
{
    lcd_set_window(x0, y0, x1, y1);
    DC_HIGH();

    uint32_t px = (x1 - x0 + 1) * (y1 - y0 + 1);
    while (px--) {
        spi_tx(color >> 8);
        spi_tx(color & 0xFF);
    }
}

/* ---------------- Draw Pixel ---------------- */
static void lcd_draw_pixel(uint16_t x, uint16_t y, uint16_t color)
{
    if (x >= LCD_W || y >= LCD_H) return;
    lcd_set_window(x, y, x, y);
    DC_HIGH();
    spi_tx(color >> 8);
    spi_tx(color & 0xFF);
}

/* ---------------- Filled Circle ---------------- */
static void lcd_fill_circle(int16_t cx, int16_t cy,
                            int16_t r, uint16_t color)
{
    for (int16_t y = -r; y <= r; y++) {
        for (int16_t x = -r; x <= r; x++) {
            if (x * x + y * y <= r * r)
                lcd_draw_pixel(cx + x, cy + y, color);
        }
    }
}

/* ---------------- Arc ---------------- */
static void lcd_draw_arc(int16_t cx, int16_t cy, int16_t r,
                         int16_t a0, int16_t a1,
                         uint16_t color)
{
    for (int16_t a = a0; a <= a1; a++) {
        float rad = a * 3.14159f / 180.0f;
        int16_t x = cx + (int16_t)(r * cosf(rad));
        int16_t y = cy + (int16_t)(r * sinf(rad));
        lcd_draw_pixel(x, y, color);
    }
}

/* ---------------- Face Clear ---------------- */
static void clear_face(int16_t cx, int16_t cy)
{
    /* clear only face interior */
    lcd_fill_circle(cx, cy, 45, YELLOW);
}

/* ---------------- Faces ---------------- */
static void face_smile(int16_t cx, int16_t cy)
{
    lcd_fill_circle(cx - 17, cy - 12, 5, BLACK);
    lcd_fill_circle(cx + 17, cy - 12, 5, BLACK);

    for (int i = 0; i < 3; i++)
        lcd_draw_arc(cx, cy + 8, 24 + i, 20, 160, BLACK);
}

static void face_angry(int16_t cx, int16_t cy)
{
    /* eyes */
    for (int i = -6; i <= 6; i++) {
        lcd_draw_pixel(cx - 17 + i, cy - 12 - i / 2, BLACK);
        lcd_draw_pixel(cx + 17 + i, cy - 12 + i / 2, BLACK);
    }

    /* mouth */
    for (int i = 0; i < 3; i++)
        lcd_draw_arc(cx, cy + 14, 24 + i, 200, 340, BLACK);
}

static void face_sad(int16_t cx, int16_t cy)
{
    lcd_fill_circle(cx - 17, cy - 12, 5, BLACK);
    lcd_fill_circle(cx + 17, cy - 12, 5, BLACK);

    for (int i = 0; i < 3; i++)
        lcd_draw_arc(cx, cy + 18, 24 + i, 200, 340, BLACK);
}

/* ---------------- Main ---------------- */
int main(void)
{
    SYSCFG_DL_init();
    DC_LOW();
    RST_HIGH();

    ili9225_init();

    /* clear screen once */
    lcd_fill_rect(0, 0, LCD_W - 1, LCD_H - 1, BLACK);

    int16_t cx = 88;
    int16_t cy = 110;

    /* draw base face once */
    lcd_fill_circle(cx, cy, 50, YELLOW);

    while (1) {
        clear_face(cx, cy);
        face_smile(cx, cy);
        delay_ms(800);

        clear_face(cx, cy);
        face_angry(cx, cy);
        delay_ms(800);

        clear_face(cx, cy);
        face_sad(cx, cy);
        delay_ms(800);
    }
}
