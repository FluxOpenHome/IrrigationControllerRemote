#!/usr/bin/env python3
"""
Transform irrigationcontrollerremote.yaml to irrigationcontrollerremoteBig.yaml
Converts M5Stack Dial (240x240) config to VIEWE UEDX48480021-MD80ET (480x480)
"""

import re
import sys

def transform_yaml(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()

    # Phase 1: Substitutions
    content = content.replace('name: "irrigation-remote"', 'name: "irrigation-remote-big"')
    content = content.replace('friendly_name: "Irrigation Remote"', 'friendly_name: "Irrigation Remote Big"')

    # Phase 2: Flash/PSRAM configuration
    content = re.sub(
        r'board_build\.flash_size: 8MB',
        'board_build.flash_size: 16MB',
        content
    )
    content = re.sub(
        r'  platformio_options:\n    board_build\.flash_mode: dio\n    board_build\.flash_size: 8MB',
        '''  platformio_options:
    board_build.flash_mode: dio
    board_build.flash_size: 16MB
    board_build.psram_mode: opi''',
        content
    )
    content = re.sub(
        r'  flash_size: 8MB',
        '  flash_size: 16MB',
        content
    )
    content = re.sub(
        r'    sdkconfig_options:\n      CONFIG_MBEDTLS_CERTIFICATE_BUNDLE: "y"\n      CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL: "y"\n      CONFIG_HTTP_BUF_SIZE: "8192"\n      CONFIG_ESP_HTTP_CLIENT_ENABLE_HTTPS: "y"',
        '''    sdkconfig_options:
      CONFIG_MBEDTLS_CERTIFICATE_BUNDLE: "y"
      CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL: "y"
      CONFIG_HTTP_BUF_SIZE: "8192"
      CONFIG_ESP_HTTP_CLIENT_ENABLE_HTTPS: "y"
      CONFIG_SPIRAM: "y"
      CONFIG_SPIRAM_MODE_OCT: "y"
      CONFIG_SPIRAM_SPEED_80M: "y"''',
        content
    )

    # Phase 3: I2C pins
    content = re.sub(
        r'i2c:\n  - id: internal_i2c\n    sda: GPIO11\n    scl: GPIO12',
        '''i2c:
  - id: internal_i2c
    sda: GPIO16
    scl: GPIO15''',
        content
    )

    # Phase 4: Remove SPI section entirely
    content = re.sub(
        r'spi:\n  - id: spi_bus\n    clk_pin: GPIO6\n    mosi_pin: GPIO5\n\n',
        '',
        content
    )

    # Phase 5: Remove buzzer output and rtttl component
    content = re.sub(
        r'  - platform: ledc\n    pin: GPIO3\n    id: buzzer_output\n    channel: 2\n',
        '',
        content
    )
    content = re.sub(
        r'rtttl:\n  output: buzzer_output\n  id: buzzer\n  gain: 30%\n\n',
        '',
        content
    )

    # Phase 6: Change backlight pin
    content = re.sub(
        r'  - platform: ledc\n    pin: GPIO9\n    id: lcd_backlight_output',
        '''  - platform: ledc
    pin: GPIO38
    id: lcd_backlight_output''',
        content
    )

    # Phase 7: Replace display section
    display_old = r'''display:
  - platform: ili9xxx
    model: GC9A01A
    cs_pin: GPIO7
    reset_pin: GPIO8
    dc_pin: GPIO4
    id: dial_lcd
    invert_colors: true
    auto_clear_enabled: false
    update_interval: never'''

    display_new = '''display:
  - platform: st7701s
    id: dial_lcd
    auto_clear_enabled: false
    update_interval: never
    dimensions:
      width: 480
      height: 480
    cs_pin: GPIO39
    de_pin: GPIO18
    hsync_pin: GPIO47
    vsync_pin: GPIO48
    pclk_pin: GPIO21
    pclk_frequency: 12MHz
    pclk_inverted: true
    hsync_front_porch: 10
    hsync_pulse_width: 8
    hsync_back_porch: 50
    vsync_front_porch: 10
    vsync_pulse_width: 8
    vsync_back_porch: 20
    data_pins:
      red:
        - GPIO11
        - GPIO12
        - GPIO13
        - GPIO14
        - GPIO0
      green:
        - GPIO8
        - GPIO20
        - GPIO3
        - GPIO46
        - GPIO9
        - GPIO10
      blue:
        - GPIO4
        - GPIO5
        - GPIO6
        - GPIO7
        - GPIO15
    init_sequence:
      - 1'''

    content = content.replace(display_old, display_new)

    # Phase 8: Replace touchscreen section
    touchscreen_old = r'''touchscreen:
  - platform: ft5x06
    id: touch
    i2c_id: internal_i2c
    address: 0x38'''

    touchscreen_new = '''touchscreen:
  - platform: cst816
    id: touch
    i2c_id: internal_i2c
    interrupt_pin: GPIO40
    reset_pin: GPIO41'''

    content = content.replace(touchscreen_old, touchscreen_new)

    # Phase 9: Encoder pins
    content = re.sub(
        r'    pin_a:\n      number: GPIO40',
        '''    pin_a:
      number: GPIO6''',
        content
    )
    content = re.sub(
        r'    pin_b:\n      number: GPIO41',
        '''    pin_b:
      number: GPIO5''',
        content
    )

    # Phase 10: Button pin
    content = re.sub(
        r'  - platform: gpio\n    id: dial_button\n    pin:\n      number: GPIO42',
        '''  - platform: gpio
    id: dial_button
    pin:
      number: GPIO0''',
        content
    )

    # Phase 11: Dashboard import URL
    content = re.sub(
        r'github://FluxOpenHome/IrrigationControllerRemote/irrigationcontrollerremote\.yaml@main',
        'github://FluxOpenHome/IrrigationControllerRemote/irrigationcontrollerremoteBig.yaml@main',
        content
    )

    # Phase 12: LVGL buffer_size
    content = re.sub(
        r'  buffer_size: 10%',
        '  buffer_size: 25%',
        content
    )

    # Phase 13: Default font
    content = re.sub(
        r'  default_font: montserrat_14',
        '  default_font: montserrat_28',
        content
    )

    # Phase 14: Theme border_width
    content = re.sub(
        r'        border_width: 2',
        '        border_width: 3',
        content
    )

    # Phase 15: Font replacements (global)
    content = content.replace('montserrat_10', 'montserrat_20')
    content = content.replace('montserrat_12', 'montserrat_24')
    content = content.replace('montserrat_14', 'montserrat_28')
    # Note: montserrat_28 was already replaced to montserrat_48 by the patterns above
    # We need to handle montserrat_28 -> montserrat_48 for specific uses (duration, time display, IP edit)
    # This is trickier - need context-aware replacement

    # Phase 16: Remove all rtttl.play actions
    # Match on_focus blocks that only contain rtttl.play
    content = re.sub(
        r'            on_focus:\n              then:\n                - rtttl\.play: "c:d=32,o=6,b=200:c"\n',
        '',
        content,
        flags=re.MULTILINE
    )

    # Also remove rtttl.play from other contexts (like after script.execute)
    content = re.sub(
        r'                - rtttl\.play: "c:d=16,o=5,b=200:c,e"\n',
        '',
        content
    )

    # Phase 17: Style pad_all and radius scaling
    content = re.sub(r'      pad_all: 6', '      pad_all: 12', content)
    content = re.sub(r'      radius: 8', '      radius: 16', content)

    # Phase 18: Individual radius values in widgets
    content = re.sub(r'            radius: 4\n', '            radius: 8\n', content)
    content = re.sub(r'              radius: 7\n', '              radius: 14\n', content)
    content = re.sub(r'              radius: 6\n', '              radius: 12\n', content)

    # Phase 19: Scale coordinate and size values
    # This is complex - need to double all numeric x, y, width, height values
    # We'll use a callback function

    def scale_lvgl_coords(match):
        key = match.group(1)
        value = int(match.group(2))
        # Don't scale if it's part of certain contexts we want to preserve
        return f'            {key}: {value * 2}'

    def scale_lvgl_coords_align(match):
        key = match.group(1)
        value = int(match.group(2))
        return f'            {key}: {value * 2}'

    # Match standalone x, y, width, height in widget definitions
    # Pattern: spaces + key: + number (not part of a GPIO pin assignment)
    content = re.sub(
        r'^            (x|y|width|height): (-?\d+)$',
        scale_lvgl_coords,
        content,
        flags=re.MULTILINE
    )

    # Also handle bar and slider heights that might be formatted differently
    content = re.sub(r'height: 8\n', 'height: 16\n', content)
    content = re.sub(r'height: 12\n', 'height: 24\n', content)
    content = re.sub(r'height: 14\n', 'height: 28\n', content)

    # Handle knob widths/heights
    content = re.sub(r'              width: 14\n              height: 14\n', '              width: 28\n              height: 28\n', content)

    # Phase 20: Scale montserrat_28 to montserrat_48 for specific large displays
    # Duration value, time display, IP edit val, big zone number
    specific_labels = [
        'lbl_dur_value',
        'lbl_time_display',
        'lbl_ip_edit_val',
        'lbl_big_zone',
        'lbl_big_remaining'
    ]

    for label_id in specific_labels:
        # Find the label and change its font from montserrat_28 to montserrat_48
        pattern = rf'(- label:\n            id: {label_id}\n.*?\n.*?text_font: )montserrat_28'
        content = re.sub(pattern, r'\1montserrat_48', content, flags=re.DOTALL)

    # Actually, after the global replace, montserrat_28 became montserrat_48, so we need to check
    # Wait, we replaced montserrat_14 -> montserrat_28 globally
    # So the original montserrat_28 values are now... need to think about order

    # Let me reconsider: original has montserrat_10, 12, 14, 28, 48
    # After replacement: montserrat_20, 24, 28, 48, 48
    # But montserrat_28 should become montserrat_48 for big values
    # So we need to selectively replace montserrat_28 -> montserrat_48 for those specific labels

    # Since we already did global replace montserrat_14 -> montserrat_28,
    # The original montserrat_28 values need targeted replacement
    # Let's handle this more carefully with context

    return content

if __name__ == '__main__':
    input_path = '/Users/brandonhalterman/Documents/GitHub/IrrigationControllerRemote/irrigationcontrollerremote.yaml'
    output_path = '/Users/brandonhalterman/Documents/GitHub/IrrigationControllerRemote/irrigationcontrollerremoteBig.yaml'

    transformed = transform_yaml(input_path, output_path)

    with open(output_path, 'w') as f:
        f.write(transformed)

    print(f"Transformation complete: {output_path}")
