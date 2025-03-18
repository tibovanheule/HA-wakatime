# Wakatime Integration for Home Assistant

This Home Assistant integration allows you to monitor your coding activity through the Wakatime API.

## Features

- Daily coding time sensor
- Top language information
- Project tracking
- Editor usage statistics
- Operating system details
- Multi-language support (English, Brazilian Portuguese)

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS > Integrations
3. Click on the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL and select "Integration" as the category
5. Click "Add"
6. Search for "Wakatime" and install it

### Manual Installation

1. Download the latest release from the releases page
2. Extract the `custom_components/wakatime` folder into your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

1. In Home Assistant, go to Configuration > Integrations
2. Click "Add Integration" and search for "Wakatime"
3. Follow the configuration steps:
   - Enter your Wakatime API key (You can find this in your Wakatime account settings)

## API Key

To obtain your Wakatime API key:

1. Log in to your Wakatime account
2. Go to [Account Settings](https://wakatime.com/settings/account)
3. Find your API Key in the "API Key" section

## Sensors

This integration provides the following sensors:

- **Daily Total**: Total coding time for the day
- **Top Language**: Your most used programming language
- **Top Project**: Your most active project
- **Top Editor**: Your most used code editor
- **Top Operating System**: Your most used operating system

## Automations

Example automation to notify you when you've been coding for too long:

```yaml
automation:
  - alias: "Coding Break Reminder"
    trigger:
      platform: numeric_state
      entity_id: sensor.wakatime_daily_total
      above: 14400  # 4 hours in seconds
    action:
      service: notify.mobile_app
      data:
        message: "You've been coding for over 4 hours today! Time for a break."
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
