import * as React from "react";
import * as ReactDOM from "react-dom";
import { BrowserRouter, Route, Routes } from 'react-router-dom'


// import { Link } from 'react-router-dom'
import { withStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
// import { withRouter } from 'react-router'


import App from './App'

const styles = {
  root: {
    flexGrow: 1,
  },
  flex: {
    flexGrow: 1,
  },

  tabLink : {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    'padding-right': 0,
    'padding-left': 0,
  }

};

const NavBarX = ({classes} : any) => {
    return (
        <div className={classes.root}>
            <AppBar position="static">
                <Tabs value={1}>
                    <Tab
                        key='Home'
                        label='home'
                        className={classes.tabLink}
                    />
                </Tabs>
            </AppBar>
        </div>
    )
}

const NavBar = withStyles(styles)(NavBarX)

ReactDOM.render(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<NavBar/>} />
      </Routes>
    </BrowserRouter>,
    document.getElementById("root")
);

