import React, { Component } from 'react'
import createStore from './global-store/createStore'
import { BrowserRouter, Route } from 'react-router-dom'


import Home from './components/Home'
import Header from './components/Header'


class App extends Component {
  componentDidMount() {
  }

  render() {
    let { store } = this.props

    return (
      <BrowserRouter basename={process.env.PUBLIC_URL}>
        <div>
          <Header/>
          <Route exact path="/" component={Home} />
        </div>
      </BrowserRouter>
    )
  }
}

const initialValue = {
}

const config = {}

export default createStore(App, initialValue, config)


