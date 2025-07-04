# CANOPEN SDK

## Installation
```
pip install -e .
```

## Enable CANable
```
source ./canable.sh
```

## Requirements
- canopen==2.3.0
- python-can==4.5.0

## Usage
```
from canopen_sdk.manager import load_motor_manager
```

## Supported Motor Drivers
| Name | Available |
|:----:|:---------:|
| [eRob](https://en.zeroerr.cn/rotary_actuators) | ✅ |
| [Elmo](https://www.elmomc.com) | ✅ |
