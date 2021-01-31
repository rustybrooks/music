#!/usr/bin/env python

import time
import instruments

l = instruments.MultiLaunchpad(number=2)

# l.send_note_on(0, 0, 127)
# l.send_note_on(4, 1, 127)
# l.send_note_on(8, 2, 127)
# l.send_note_on(12, 3, 127)

# l.send_cc(2, 127)
# l.send_cc(13, 127)

l.send_cc2(2, 127)
l.send_cc2(15, 127)

while True:
    time.sleep(0.5)
