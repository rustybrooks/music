import React, { Component } from 'react'

class App extends Component {
  componentDidMount() {
  }

  render() {
    console.log('...', navigator.requestMIDIAccess)

    return (
      <div>Hi</div>
    )
  }
}

export default App


