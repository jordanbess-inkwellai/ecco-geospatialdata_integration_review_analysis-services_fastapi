import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Toolbar,
  Tooltip,
  Collapse
} from '@mui/material';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import Link from 'next/link';
import { useRouter } from 'next/router';
import MapIcon from '@mui/icons-material/Map';
import LayersIcon from '@mui/icons-material/Layers';
import StorageIcon from '@mui/icons-material/Storage';
import SettingsIcon from '@mui/icons-material/Settings';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import TransformIcon from '@mui/icons-material/Transform';
import CodeIcon from '@mui/icons-material/Code';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import CloudIcon from '@mui/icons-material/Cloud';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import DataUsageIcon from '@mui/icons-material/DataUsage';
import TerrainIcon from '@mui/icons-material/Terrain';
import DescriptionIcon from '@mui/icons-material/Description';
import TableChartIcon from '@mui/icons-material/TableChart';
import { useAIFeatures } from '../../hooks/useAIFeatures';

const drawerWidth = 240;

interface SidebarProps {
  mobileOpen: boolean;
  handleDrawerToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, handleDrawerToggle }) => {
  const router = useRouter();
  const { aiEnabled, loading: aiLoading } = useAIFeatures();
  const [openSubMenus, setOpenSubMenus] = useState<{ [key: string]: boolean }>({});

  // Define base menu items that are always shown
  const baseMenuItems = [
    { text: 'Dashboard', href: '/', icon: <DashboardIcon /> },
    { text: 'Map', href: '/map', icon: <MapIcon /> },
    { text: 'Layers', href: '/layers', icon: <LayersIcon /> },
    { text: 'Martin', href: '/martin', icon: <TerrainIcon /> },
    { text: 'Processes', href: '/processes', icon: <AnalyticsIcon /> },
    { text: 'Data Processing', href: '/data-processing', icon: <TransformIcon /> },
    { text: 'Workflows', href: '/workflows', icon: <PlayArrowIcon /> },
    { text: 'DuckDB', href: '/duckdb', icon: <DataUsageIcon /> },
    { text: 'DocETL', href: '/docetl', icon: <DescriptionIcon /> },
    { text: 'Querybook', href: '/querybook', icon: <TableChartIcon /> },
    { text: 'Box.com', href: '/box-integration', icon: <CloudIcon /> },
    {
      text: 'Rclone',
      href: '/rclone/browser',
      icon: <CloudIcon />,
      subItems: [
        { text: 'File Browser', href: '/rclone/browser' },
        { text: 'Configuration', href: '/rclone/config' },
        { text: 'Box.com Integration', href: '/rclone/box' },
      ]
    },
    { text: 'Database', href: '/database', icon: <StorageIcon /> },
    { text: 'Notebooks', href: '/notebooks', icon: <CodeIcon /> },
    { text: 'Settings', href: '/settings', icon: <SettingsIcon /> },
  ];

  // Define AI-specific menu items that are only shown when AI is enabled
  const aiMenuItems = [
    { text: 'AI Tools', href: '/ai-tools', icon: <SmartToyIcon /> },
  ];

  // Combine menu items based on AI availability
  const menuItems = aiEnabled
    ? [...baseMenuItems.slice(0, 9), ...aiMenuItems, ...baseMenuItems.slice(9)]
    : baseMenuItems;

  // Filter out Querybook and DocETL if they're not enabled
  const filteredMenuItems = menuItems.filter(item => {
    if (item.href === '/querybook' && process.env.NEXT_PUBLIC_QUERYBOOK_ENABLED !== 'true') {
      return false;
    }
    if (item.href === '/docetl' && process.env.NEXT_PUBLIC_DOCETL_ENABLED !== 'true') {
      return false;
    }
    return true;
  });

  const handleToggleSubMenu = (text: string) => {
    setOpenSubMenus(prev => ({
      ...prev,
      [text]: !prev[text]
    }));
  };

  const isSubMenuOpen = (text: string) => !!openSubMenus[text];

  const isItemActive = (href: string) => {
    return router.pathname === href || router.pathname.startsWith(`${href}/`);
  };

  const renderMenuItem = (item: any) => {
    const hasSubItems = item.subItems && item.subItems.length > 0;

    if (hasSubItems) {
      return (
        <React.Fragment key={item.text}>
          <ListItem disablePadding>
            <ListItemButton
              onClick={() => handleToggleSubMenu(item.text)}
              selected={isItemActive(item.href)}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
              {isSubMenuOpen(item.text) ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
          </ListItem>
          <Collapse in={isSubMenuOpen(item.text)} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.subItems.map((subItem: any) => (
                <ListItem key={subItem.text} disablePadding>
                  <Link href={subItem.href} passHref style={{ textDecoration: 'none', width: '100%', color: 'inherit' }}>
                    <ListItemButton
                      selected={router.pathname === subItem.href}
                      sx={{ pl: 4 }}
                    >
                      <ListItemText primary={subItem.text} />
                    </ListItemButton>
                  </Link>
                </ListItem>
              ))}
            </List>
          </Collapse>
        </React.Fragment>
      );
    }

    return (
      <ListItem key={item.text} disablePadding>
        <Link href={item.href} passHref style={{ textDecoration: 'none', width: '100%', color: 'inherit' }}>
          <ListItemButton selected={isItemActive(item.href)}>
            <ListItemIcon>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItemButton>
        </Link>
      </ListItem>
    );
  };

  const drawer = (
    <div>
      <Toolbar />
      <Divider />
      <List>
        {filteredMenuItems.map(renderMenuItem)}
      </List>
    </div>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      aria-label="mailbox folders"
    >
      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
      >
        {drawer}
      </Drawer>

      {/* Desktop drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
        open
      >
        {drawer}
      </Drawer>
    </Box>
  );
};

export default Sidebar;
