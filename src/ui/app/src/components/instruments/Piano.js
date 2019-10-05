import React, { useState, useEffect } from 'react';

import MidiMonitor from "../MidiMonitor"
import MidiInputs from "../MidiInputs"

const Piano = () => {
  return <div>
    <MidiMonitor/>
    <MidiInputs/>
  </div>
}

export default Piano