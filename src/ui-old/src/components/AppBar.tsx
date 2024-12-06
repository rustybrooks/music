import './AppBar.css';

export function AppBar() {
  return (
    <div style={{ width: '100%' }}>
      <header className="appbar-header">
        <div style={{ display: 'flex' }}>
          <div style={{ display: 'flex', flexGrow: 2 }}>
            <div className="appbar-menu">
              <a className="appbar-button" tabIndex={0} href="/">
                Home
              </a>
            </div>
            <div className="appbar-menu">
              <a className="appbar-button" tabIndex={0} href="/torso">
                Torso
              </a>
            </div>
          </div>
        </div>
      </header>
    </div>
  );
}
