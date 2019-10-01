import React from 'react'
import Paper from '@material-ui/core/Paper'
import { withStyles } from '@material-ui/core/styles'
import { withStore } from '../global-store'

const style = theme => ({
  'paper': {

  }
});

class Home extends React.Component {
  componentDidMount() {
    console.log(navigator.requestMIDIAccess)
    console.log(window.navigator.requestMIDIAccess)
  }

  render() {
    const { classes } = this.props

    return (
      <div>
        <Paper className={classes.paper}>
          Hi
        </Paper>
      </div>
    )
  }
}

export default withStore(withStyles(style)(Home))



