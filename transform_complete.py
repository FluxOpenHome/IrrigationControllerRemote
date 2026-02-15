#!/usr/bin/env python3
"""
Complete transformation: irrigationcontrollerremote.yaml -> irrigationcontrollerremoteBig.yaml
M5Stack Dial (240x240) -> VIEWE UEDX48480021-MD80ET (480x480)
"""

import re

def transform_file():
    input_file = '/Users/brandonhalterman/Documents/GitHub/IrrigationControllerRemote/irrigationcontrollerremote.yaml'
    output_file = '/Users/brandonhalterman/Documents/GitHub/IrrigationControllerRemote/irrigationcontrollerremoteBig.yaml'

    with open(input_file, 'r') as f:
        lines = f.readlines()

    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        orig_line = line

        # CRITICAL: Font replacements MUST happen in specific order to avoid double-replacement
        # We need to handle montserrat_28 -> montserrat_48 for SPECIFIC labels BEFORE global replace
        # Track context to know if we're in a specific label

        # For now, let's do global font replacement, then fix specific ones
        line = line.replace('montserrat_10', 'MONTSERRAT_10_TEMP')
        line = line.replace('montserrat_12', 'MONTSERRAT_12_TEMP')
        line = line.replace('montserrat_14', 'MONTSERRAT_14_TEMP')
        line = line.replace('montserrat_28', 'MONTSERRAT_28_TEMP')
        line = line.replace('montserrat_48', 'montserrat_48')  # Keep as is

        # Now map to scaled versions
        line = line.replace('MONTSERRAT_10_TEMP', 'montserrat_20')
        line = line.replace('MONTSERRAT_12_TEMP', 'montserrat_24')
        line = line.replace('MONTSERRAT_14_TEMP', 'montserrat_28')
        line = line.replace('MONTSERRAT_28_TEMP', 'montserrat_48')  # Default: 28->48

        # Substitutions
        if 'name: "irrigation-remote"' in line and 'friendly' not in line:
            line = line.replace('name: "irrigation-remote"', 'name: "irrigation-remote-big"')
        elif 'friendly_name: "Irrigation Remote"' in line:
            line = line.replace('friendly_name: "Irrigation Remote"', 'friendly_name: "Irrigation Remote Big"')

        # Flash/PSRAM
        elif 'board_build.flash_size: 8MB' in line:
            line = line.replace('8MB', '16MB')
        elif 'flash_size: 8MB' in line:
            line = line.replace('8MB', '16MB')
        elif line.strip() == 'board_build.flash_mode: dio':
            result.append(line)
            i += 1
            # Add flash_size line
            result.append(lines[i])  # board_build.flash_size: 16MB
            i += 1
            # Add psram line
            result.append('    board_build.psram_mode: opi\n')
            continue
        elif line.strip() == 'CONFIG_ESP_HTTP_CLIENT_ENABLE_HTTPS: "y"':
            result.append(line)
            i += 1
            # Add SPIRAM config
            result.append('      CONFIG_SPIRAM: "y"\n')
            result.append('      CONFIG_SPIRAM_MODE_OCT: "y"\n')
            result.append('      CONFIG_SPIRAM_SPEED_80M: "y"\n')
            continue

        # I2C pins
        elif 'sda: GPIO11' in line:
            line = line.replace('GPIO11', 'GPIO16')
        elif 'scl: GPIO12' in line:
            line = line.replace('GPIO12', 'GPIO15')

        # SPI section - SKIP entirely
        elif line.strip() == 'spi:':
            # Skip spi section (4 lines)
            i += 4
            continue

        # Remove buzzer output
        elif 'id: buzzer_output' in line:
            # Skip buzzer output (4 lines back to start)
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('display:'):
                i += 1
            i -= 1  # Back up one since loop will increment
            result.append('\n')
            i += 1
            continue

        # Remove rtttl section
        elif line.strip().startswith('rtttl:'):
            # Skip rtttl section
            i += 1
            while i < len(lines) and lines[i].startswith('  ') and not lines[i].strip().startswith('#'):
                i += 1
            i -= 1
            result.append('\n')
            i += 1
            continue

        # Backlight pin
        elif 'pin: GPIO9' in line and 'lcd_backlight_output' in lines[i+1]:
            line = line.replace('GPIO9', 'GPIO38')

        # Display section - complete replacement
        elif line.strip() == 'display:':
            result.append('display:\n')
            result.append('  - platform: st7701s\n')
            result.append('    id: dial_lcd\n')
            result.append('    auto_clear_enabled: false\n')
            result.append('    update_interval: never\n')
            result.append('    dimensions:\n')
            result.append('      width: 480\n')
            result.append('      height: 480\n')
            result.append('    cs_pin: GPIO39\n')
            result.append('    de_pin: GPIO18\n')
            result.append('    hsync_pin: GPIO47\n')
            result.append('    vsync_pin: GPIO48\n')
            result.append('    pclk_pin: GPIO21\n')
            result.append('    pclk_frequency: 12MHz\n')
            result.append('    pclk_inverted: true\n')
            result.append('    hsync_front_porch: 10\n')
            result.append('    hsync_pulse_width: 8\n')
            result.append('    hsync_back_porch: 50\n')
            result.append('    vsync_front_porch: 10\n')
            result.append('    vsync_pulse_width: 8\n')
            result.append('    vsync_back_porch: 20\n')
            result.append('    data_pins:\n')
            result.append('      red:\n')
            result.append('        - GPIO11\n')
            result.append('        - GPIO12\n')
            result.append('        - GPIO13\n')
            result.append('        - GPIO14\n')
            result.append('        - GPIO0\n')
            result.append('      green:\n')
            result.append('        - GPIO8\n')
            result.append('        - GPIO20\n')
            result.append('        - GPIO3\n')
            result.append('        - GPIO46\n')
            result.append('        - GPIO9\n')
            result.append('        - GPIO10\n')
            result.append('      blue:\n')
            result.append('        - GPIO4\n')
            result.append('        - GPIO5\n')
            result.append('        - GPIO6\n')
            result.append('        - GPIO7\n')
            result.append('        - GPIO15\n')
            result.append('    init_sequence:\n')
            result.append('      - 1\n')
            # Skip old display section (8 lines)
            i += 8
            continue

        # Touchscreen section - complete replacement
        elif line.strip() == 'touchscreen:':
            result.append('touchscreen:\n')
            result.append('  - platform: cst816\n')
            result.append('    id: touch\n')
            result.append('    i2c_id: internal_i2c\n')
            result.append('    interrupt_pin: GPIO40\n')
            result.append('    reset_pin: GPIO41\n')
            # Skip old touchscreen section (4 lines)
            i += 4
            continue

        # Encoder pins
        elif 'number: GPIO40' in line and i > 0 and 'pin_a:' in lines[i-1]:
            line = line.replace('GPIO40', 'GPIO6')
        elif 'number: GPIO41' in line and i > 0 and 'pin_b:' in lines[i-1]:
            line = line.replace('GPIO41', 'GPIO5')

        # Button pin
        elif 'number: GPIO42' in line and i > 0 and 'dial_button' in lines[i-4]:
            line = line.replace('GPIO42', 'GPIO0')

        # Dashboard import
        elif 'irrigationcontrollerremote.yaml@main' in line:
            line = line.replace('irrigationcontrollerremote.yaml', 'irrigationcontrollerremoteBig.yaml')

        # LVGL buffer
        elif 'buffer_size: 10%' in line:
            line = line.replace('10%', '25%')

        # Theme border_width (in focused section)
        elif 'border_width: 2' in line and '      ' in line[:10]:
            line = line.replace('border_width: 2', 'border_width: 3')

        # Style definitions
        elif 'pad_all: 6' in line:
            line = line.replace('pad_all: 6', 'pad_all: 12')
        elif line.strip() == 'radius: 8':
            line = line.replace('radius: 8', 'radius: 16')
        elif line.strip() == 'radius: 4':
            line = line.replace('radius: 4', 'radius: 8')
        elif line.strip() == 'radius: 7':
            line = line.replace('radius: 7', 'radius: 14')
        elif line.strip() == 'radius: 6':
            line = line.replace('radius: 6', 'radius: 12')
        elif 'border_width: 2' in line:
            line = line.replace('border_width: 2', 'border_width: 3')

        # Remove rtttl.play calls (on_focus blocks)
        elif 'rtttl.play:' in line:
            # Skip this line and check if prev line was "then:"
            i += 1
            continue

        # Scale coordinates and sizes (x, y, width, height)
        # Must be careful with GPIO pins!
        elif re.match(r'^(\s+)(x|y|width|height): (-?\d+)\s*$', line):
            match = re.match(r'^(\s+)(x|y|width|height): (-?\d+)\s*$', line)
            if match:
                indent = match.group(1)
                key = match.group(2)
                value = int(match.group(3))
                scaled = value * 2
                line = f'{indent}{key}: {scaled}\n'

        # Special height values for bars/sliders
        elif re.match(r'^(\s+height: )(8|12|14)(\s*)$', line):
            match = re.match(r'^(\s+height: )(\d+)(\s*)$', line)
            if match:
                prefix = match.group(1)
                value = int(match.group(2))
                suffix = match.group(3)
                line = f'{prefix}{value * 2}{suffix}\n'

        # Knob width/height
        elif re.match(r'^(\s+width: )(14)(\s*)$', line) and i + 1 < len(lines) and 'height: 14' in lines[i + 1]:
            line = line.replace('width: 14', 'width: 28')

        result.append(line)
        i += 1

    # Write output
    with open(output_file, 'w') as f:
        f.writelines(result)

    print(f"Transformed {len(result)} lines")
    print(f"Output: {output_file}")

if __name__ == '__main__':
    transform_file()
