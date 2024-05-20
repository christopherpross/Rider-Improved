# Rider-Improved
An addon for the Screenreader [NVDA](https://github.com/nvaccess/nvda) to improve the accessibility of [JetBrains Rider](https://www.jetbrains.com/rider/).

JetBrains Rider is a powerful IDE, but its accessibility features are not ideal for users relying on screen readers. This addon aims to bridge that gap by enhancing the accessibility of Rider, making critical information more easily accessible and improving the overall user experience for visually impaired developers.

This addon is distributed under the terms of the GNU General Public License, version 2 or later. Please see the file COPYING.txt for further details.

## Installation

You can install the Rider-Improved addon in two ways:

1. **NVDA Addon Store**:
   - Download the addon directly from the NVDA Addon Store.

2. **GitHub Releases**:
   - Go to the [GitHub releases page](https://github.com/christopherpross/Rider-Improved/releases) of this project.
   - Download the latest release `.nvda-addon` file.
   - open the downloaded file with NVDA
   - Follow the prompts to complete the installation.

After installing the addon, please follow the setup instructions below to configure JetBrains Rider properly.

## Features

This addon provides the following features you can use in JetBrains Rider:

* The addon reads out automaticly or manualy the status bar of Rider, there Rider provides useful informations like the error/warning for the current line and more.
* You can use NVDA+d to read the documentation for a code completion item

... and more features and improvements are planned!


## Requirements

This addon is tested with JetBrains Rider 2024.1 older or newer versions could break this addon.

## Rider setup

Please configure Rider as follows:

1. **Enable Accessibility Support**:
   - Press `Ctrl+Alt+S` to open the settings.
   - Under 'Appearance & Behavior' -> 'Appearance', check the option 'Support screen readers'.
   - Click 'Apply', followed by 'OK'.

2. **Enable the Status Bar**:
   - Open a solution in Rider.
   - Press `Alt+V` to focus the 'View' menu.
   - Activate 'Appearance' -> 'Status Bar'.


## Contribution Guidelines

We welcome contributions to the Rider-Improved addon! If you encounter any issues or have suggestions for improvements, please use the following methods to get in touch or contribute:

1. **Report Issues**:
   - If you find any bugs or have issues, please report them on the [GitHub Issues](https://github.com/your-repository/issues) page.

2. **Contact**:
   - You can also reach out via the email address provided in the addon for any questions or support.

3. **Submit Pull Requests**:
   - If you have enhancements or bug fixes, feel free to submit a pull request. We appreciate all contributions and look forward to your input.

Thank you for your interest in improving the Rider-Improved addon!
