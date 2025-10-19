# Smart Tank Monitor v2.0

A comprehensive tank monitoring and simulation system designed for instrumentation engineering applications, featuring real-time level monitoring, automated valve control, and data logging capabilities.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.0%2B-green)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Application in Instrumentation Engineering](#application-in-instrumentation-engineering)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Technical Details](#technical-details)
- [CSV Log Format](#csv-log-format)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Desktop application that simulates and monitors industrial tank systems with real-time visualization, automated valve control, alarm management, and comprehensive data logging.

**Use Cases:**
- Training instrumentation engineers on tank monitoring systems
- Simulating SCADA operations
- Testing control algorithms before field deployment
- Process control education
- Prototyping tank management systems

---

## ✨ Features

- **Multi-Tank Management**: Monitor and control multiple tanks simultaneously
- **Real-Time Simulation**: Physics-based fluid filling and draining calculations
- **Automated Valve Control**: Opens/closes valves based on target levels
- **Alarm System**: Alerts for critically low (<10 cm) or high (>190 cm) levels
- **User Authentication**: Login system with user tracking for audit trails
- **Data Logging**: Automatic CSV logging with timestamps
- **Export Functionality**: Download complete operation logs
- **Configurable Parameters**: Radius (1-1000 cm), Target Level (0-200 cm), Flow Rate (0-50 L/min)
- **Multiple Fluid Types**: Water, Oil, Diesel
- **Visual Indicators**: Color-coded valve states (GREEN=OPEN, RED=CLOSED)

---

## 🔧 Application in Instrumentation Engineering

### Real-World Applications
Simulates tank level control systems found in water treatment plants, chemical processing facilities, oil refineries, food manufacturing, and pharmaceutical production.

### Key Uses
- **SCADA Prototyping**: Test control logic before field implementation
- **PID Testing**: Understand level control dynamics and validate algorithms
- **Safety Simulation**: High/low level alarms, automatic shutoff, leak detection
- **Data Analysis**: Historical trends, performance monitoring, compliance documentation
- **Training**: Practice HMI concepts and data acquisition procedures

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps
```bash
# Install dependencies
pip install PySide6

# Run application
python tank_monitor.py
```

### Optional: Theme Setup
1. Create `themes` folder in application directory
2. Add `dracula.qss` file for custom theme

---

## 📖 Usage Guide

### Quick Start
1. **Login**: Enter your username
2. **Add Tank**: Fill in parameters (Tank ID, Fluid Type, Radius, Target Level, Flow Rate) and click "Add Tank"
3. **Start Simulation**: Click "Start Simulation" to begin monitoring
4. **Monitor**: Observe real-time level updates, valve status, and volume calculations
5. **Stop**: Click "Stop Simulation" to pause
6. **Download Logs**: Click "📥 Download CSV Logs" to export data

### Managing Tanks
- **Update**: Select a tank row, modify parameters, click "Update Tank"
- **Delete**: Select a tank row, click "Delete Tank"
- **Clear**: Click "Clear Fields" to reset form

### Understanding the Display
- **Green Valve**: OPEN (filling)
- **Red Valve**: CLOSED (target reached)
- **Brown Highlight**: Alarm condition (level <10 cm or >190 cm)
- **Last Modified By**: Shows which user last updated the tank

---

## 🔬 Technical Details

### Volume Calculation
```
Volume (L) = π × r² × h × 1000
```
Where r and h are in meters (converted from cm input)

### Fill Time Formula
```
Time (seconds) = Volume (L) / (Flow Rate (L/min) / 60)
```

**Example**: Tank with radius=10cm, height=10cm, flow=10L/min
- Volume = 3.142 L
- Fill Time ≈ 18.85 seconds

### Simulation Parameters
- **Timer Interval**: 1.5 seconds
- **Level Increase**: Calculated from flow rate and time interval
- **Level Decrease**: 0.1-0.5 cm random (simulates evaporation/consumption)
- **Alarm Thresholds**: Low <10 cm, High >190 cm

---

## 📊 CSV Log Format

| Column | Description | Example |
|--------|-------------|---------|
| Timestamp | Date and time | 2025-10-19 15:30:45 |
| Tank ID | Unique identifier | TANK-101 |
| Fluid Type | Type of fluid | Water |
| Radius (cm) | Tank radius | 50.0 |
| Level (cm) | Current level | 45.32 |
| Volume (L) | Calculated volume | 353.8 |
| Valve Status | OPEN or CLOSED | OPEN |
| Target (cm) | Target setpoint | 100 |
| Flow Rate (L/min) | Inlet flow rate | 10 |
| Last Modified By | Username | arya_p |

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Application won't start | Verify Python 3.8+ and PySide6 installed |
| Simulation not updating | Add at least one tank, ensure flow rate >0 |
| CSV download fails | Run simulation first to generate logs |
| Alarms trigger immediately | Initial level is 0 cm (expected behavior) |
| Incorrect fill times | Verify radius, target level, and flow rate values |

### Performance Tips
- Limit to 50 tanks for optimal performance
- Clear old CSV logs periodically
- Use SSD storage for faster operations

---


---

## 📧 Contact & Support

For questions or issues:
- Create an issue on GitHub
 https://github.com/aryapakhare

---

## Quick Reference

```bash
# Installation
pip install PySide6

# Run
python tank_monitor.py

# View logs
cat tank_logs.csv
```

---

**Last Updated:** October 2025
**Instrumentation Engineering Application**

*Happy Monitoring! 🚰📊*
