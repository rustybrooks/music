import React from 'react'
import { withStyles } from '@material-ui/core/styles'
import Toolbar from '@material-ui/core/Toolbar'
import Button from '@material-ui/core/Button'
import { Link } from 'react-router-dom'
import AppBar from '@material-ui/core/AppBar'
import Drawer from '@material-ui/core/Drawer'
import { makeStyles } from '@material-ui/core/styles';

import { withStore } from '../global-store'

const style = theme => ({
  root: {
    flexGrow: 1,
  },
  menuButton: {
    // marginRight: theme.spacing(2),
  },
  title: {
    flexGrow: 1,
  },
})

class Header extends React.Component {
  state = {
    'anchorEl': null,
  }

  toggleDrawerEvent(open) {
    return event => {
      if (event.type === 'keydown' && (event.key !== 'Escape')) {
        return;
      }
      this.toggleDrawer(open)
    }
  };

  toggleDrawer(open) {
  }

  componentDidMount() {
    const { store } = this.props
  }

  render() {
    const { classes } = this.props
    return (
      <div className={classes.root}>
        <AppBar position="static">
          <Toolbar>
            <Button color="inherit" component={Link} to="/">Home</Button>
          </Toolbar>
        </AppBar>
        <Drawer anchor="top" open={false} onClose={this.toggleDrawerEvent(false)}>
          <div
              role="presentation"
            >
          </div>
        </Drawer>
      </div>
    )
  }
}

export default withStore(withStyles(style)(Header))
