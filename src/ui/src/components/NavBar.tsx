import { rem, Stack, Tooltip, UnstyledButton } from '@mantine/core';
import { useLocation, useNavigate } from 'react-router-dom';
import classes from './NavBar.module.css';
import { icons } from '../constants/icons';

interface NavbarLinkProps {
  icon: typeof icons.home;
  label: string;
  active?: boolean;

  onClick?(): void;
}

function NavbarLink({ icon: Icon, label, active, onClick }: NavbarLinkProps) {
  return (
    <Tooltip label={label} position="right" transitionProps={{ duration: 0 }}>
      <UnstyledButton onClick={onClick} className={classes.link} data-active={active || undefined}>
        <Icon style={{ width: rem(30), height: rem(30) }} stroke={1.5} />
      </UnstyledButton>
    </Tooltip>
  );
}

const menuItems = [
  { icon: icons.home, label: 'Home', url: '/' },
  { icon: icons.torso, label: 'Torso', url: '/torso' },
];

export const NavBar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const links = menuItems.map(link => (
    <NavbarLink {...link} key={link.label} active={location.pathname === link.url} onClick={() => navigate(link.url)} />
  ));

  return (
    <nav className={classes.navbar}>
      <div className={classes.navbarMain}>
        <Stack justify="center" gap={0}>
          {links}
        </Stack>
      </div>
    </nav>
  );
};
