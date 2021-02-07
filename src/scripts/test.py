#!/usr/bin/env python

import time
from miditool import instruments

lp = instruments.MultiLaunchpad(
    number=2,
    modes=[
        instruments.MLMPianoMode()
    ],
    start_mode=0,
)

while True:
    time.sleep(0.1)
