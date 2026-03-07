<p align="center">
<img src="https://user-images.githubusercontent.com/466460/175781161-dd70c5b4-d45a-4cdb-bf57-d4fd7fbedb0b.png" width="125">
</p>

<h1 align="center">Alarm.com for Home Assistant</h1>

<p align="center">
Unofficial Home Assistant integration for Alarm.com
</p>

<p align="center">
This project is not affiliated with Alarm.com
</p>

<br/>

---

## Maintained Fork

This repository is an actively maintained fork of the original Alarm.com Home Assistant integration.

The purpose of this fork is to maintain compatibility with modern Home Assistant releases and continue development of the integration as the Home Assistant platform evolves.

Recent Home Assistant updates introduced architectural changes that affect this integration. This fork ensures the integration continues to function reliably while adapting to those changes, including upcoming device registry enforcement requirements in Home Assistant 2025.12.

Project home and issue tracking:

https://github.com/ibasebcast/ha-alarmdotcom

The maintainer of this fork operates Alarm.com systems professionally and has access to Alarm.com hardware and environments that allow broader testing across device types and system configurations.

Community feedback and testing are welcome.

---

<p align="center">
  <a href="https://github.com/ibasebcast/ha-alarmdotcom/actions/workflows/hassfest.yaml"><img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/ibasebcast/ha-alarmdotcom/hassfest.yaml"></a>
  <a href="https://results.pre-commit.ci/latest/github/ibasebcast/ha-alarmdotcom/main"><img src="https://results.pre-commit.ci/badge/github/ibasebcast/ha-alarmdotcom/main.svg" /></a>
  <a href="https://github.com/ibasebcast/ha-alarmdotcom/commits/main"><img src="https://img.shields.io/github/commit-activity/y/ibasebcast/ha-alarmdotcom.svg" /></a>
</p>

<p align="center">
  <a href="https://hacs.xyz"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" /></a>
  <a href="https://github.com/ibasebcast/ha-alarmdotcom/releases"><img src="https://img.shields.io/github/release/ibasebcast/ha-alarmdotcom.svg" /></a>
  <a href="https://github.com/ibasebcast/ha-alarmdotcom/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/ibasebcast/ha-alarmdotcom"></a>
</p>

---

## Overview

This custom component allows Home Assistant to interface with [Alarm.com](https://www.alarm.com/) using the Alarm.com website's unofficial API.

The integration focuses primarily on Alarm.com security system functionality and requires an Alarm.com service package that includes security system support.

Because this integration communicates with Alarm.com using unofficial endpoints, functionality may change or break if Alarm.com modifies their platform.

---

![image](https://user-images.githubusercontent.com/466460/171702200-c5edd68b-c54f-4ca4-82b3-d5a0bb97702b.png)

![image](https://user-images.githubusercontent.com/466460/171701963-e5b5f765-6817-4313-8fa1-6035f4c453e9.png)

---

# Safety Warnings

This integration is great for casual use within Home Assistant but **should not be relied upon for safety-critical functions.**

Reasons include:

1. This integration communicates with Alarm.com using an unofficial API which may change at any time.
2. Status updates from Alarm.com may take several minutes to propagate.
3. Home Assistant automations may introduce unexpected behavior.
4. This code is community-developed and may contain bugs.

For safety notifications such as:

- Break-ins
- Fire
- Carbon monoxide
- Water leaks
- Freeze sensors

You should rely on **Alarm.com's official applications and services.**

Where possible, use **locally controlled devices supported directly by Home Assistant** for automation. Local integrations continue functioning during internet outages whereas this integration depends on cloud communication.

---

# Supported Devices

| Device Type | Actions | View Status | Low Battery | Malfunction | Notes |
|-------------|--------|------------|-------------|-------------|------|
| Alarm System | Arm Away, Arm Stay, Arm Night, Disarm | ✔ | ✔ | ✔ | |
| Garage Door | Open, Close | ✔ | ✔ | ✔ | |
| Gate | Open, Close | ✔ | ✔ | ✔ | |
| Light | On / Off / Brightness | ✔ | ✔ | ✔ | |
| Lock | Lock, Unlock | ✔ | ✔ | ✔ | |
| Sensor | None | ✔ | ✔ | ✔ | Contact sensors will not report repeated changes within a 3 minute window |
| Thermostat | Heat, Cool, Auto, Fan | ✔ | ✔ | ✔ | Fan-only mode runs for the maximum duration supported by Alarm.com |

---

# Supported Sensor Types

| Sensor Type | Notes |
|--------------|------|
| Contact | Doors, windows |
| Freeze | |
| Glass Break / Vibration | Includes standalone and panel-integrated sensors |
| Motion | |
| Vibration Contact | Doors, safes, windows |
| Water | |

Alarm.com may use different internal identifiers for sensors and not all have been documented. If a supported sensor does not appear in Home Assistant, please open an issue.

https://github.com/ibasebcast/ha-alarmdotcom/issues

---

# Installation

## Install Using HACS (Recommended)

This integration can be installed through HACS using a custom repository.

1. Open **HACS**
2. Navigate to **Integrations**
3. Click the **three-dot menu**
4. Select **Custom repositories**
5. Add the repository URL: https://github.com/ibasebcast/ha-alarmdotcom
6. Select **Integration** as the category
7. Click **Add**
8. Install **Alarm.com**
9. Restart Home Assistant

After restarting:

**Settings → Devices & Services → Add Integration → Alarm.com**

---

# Configuration

When adding the integration you will be prompted for the following parameters:

| Parameter | Required | Description |
|----------|----------|------------|
| Username | Yes | Alarm.com account username |
| Password | Yes | Alarm.com account password |
| One-Time Password | Optional | Required for accounts with two-factor authentication |

---

# Integration Options

These settings can be modified later using the **Configure** button on the Alarm.com integration card.

| Parameter | Description |
|----------|------------|
| Code | Code required for disarming or unlocking via Home Assistant |
| Force Bypass | Bypass open zones when arming |
| No Entry Delay | Skip entry delay sensors |
| Silent Arming | Suppress panel beeps when arming |

Note that some Alarm.com providers restrict combinations of these options.

---

# Development Status

This integration is under active maintenance.

Recent work includes:

- Restoring compatibility with modern Home Assistant releases
- Fixing entity availability issues
- Updating device registry usage to comply with upcoming Home Assistant requirements
- Improving websocket connection reliability

Additional improvements and device support are planned.

Community testing and feedback are welcome.

---

# Contributing

Issues and pull requests are welcome.

Please open issues here:

https://github.com/ibasebcast/ha-alarmdotcom/issues

If you are reporting a bug, include:

- Home Assistant version
- Integration version
- Logs from Home Assistant

---

# License

This project is licensed under the MIT License.

See the LICENSE file for details.