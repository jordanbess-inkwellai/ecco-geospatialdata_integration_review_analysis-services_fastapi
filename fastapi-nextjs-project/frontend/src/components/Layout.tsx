import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

interface NavItem {
    name: string;
    path: string;
    icon: string;
}

const navItems: NavItem[] = [
    { name: 'Dashboard', path: '/', icon: 'home' },
    { name: 'Geospatial', path: '/geospatial', icon: 'map' },
    { name: 'Importer', path: '/importer', icon: 'upload' },
    { name: 'Geo Features', path: '/geo-feature', icon: 'layers' },
    { name: 'Geo Tables', path: '/geo-table', icon: 'table' },
    { name: 'Geo Suitability', path: '/geo-suitability', icon: 'check-circle' },
    { name: 'Tile Converter', path: '/tile-converter', icon: 'grid_3x3' },
    { name: 'Tile Uploader', path: '/tile-uploader', icon: 'cloud_upload' },
    { name: 'Database Monitor', path: '/database-monitor', icon: 'storage' },
    { name: 'Workflows', path: '/workflows', icon: 'workflow' },
    { name: 'Scripts', path: '/scripts', icon: 'code' },
    { name: 'Metadata', path: '/metadata', icon: 'description' },
    { name: 'Developer', path: '/developer', icon: 'code' },
    { name: 'Settings', path: '/settings', icon: 'settings' },
];

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const router = useRouter();

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    return (
        <div className="layout">
            <header className="header">
                <div className="header-content">
                    <button className="menu-button" onClick={toggleSidebar}>
                        <span className="material-icons">menu</span>
                    </button>
                    <h1>Integrated Geospatial API</h1>
                </div>
            </header>

            <div className="container">
                <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
                    <nav>
                        <ul>
                            {navItems.map((item) => (
                                <li key={item.path} className={router.pathname === item.path ? 'active' : ''}>
                                    <Link href={item.path}>
                                        <a>
                                            <span className="material-icons">{item.icon}</span>
                                            <span className="nav-text">{item.name}</span>
                                        </a>
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </nav>
                </aside>

                <main className={`main-content ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
                    {children}
                </main>
            </div>

            <footer className="footer">
                <p>&copy; {new Date().getFullYear()} Integrated Geospatial API</p>
            </footer>

            {/* Add Material Icons */}
            <link
                href="https://fonts.googleapis.com/icon?family=Material+Icons"
                rel="stylesheet"
            />

            <style jsx>{`
                .layout {
                    display: flex;
                    flex-direction: column;
                    min-height: 100vh;
                }

                .header {
                    background-color: #0070f3;
                    color: white;
                    padding: 1rem;
                    position: sticky;
                    top: 0;
                    z-index: 100;
                }

                .header-content {
                    display: flex;
                    align-items: center;
                }

                .menu-button {
                    background: none;
                    border: none;
                    color: white;
                    margin-right: 1rem;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                }

                .container {
                    display: flex;
                    flex: 1;
                }

                .sidebar {
                    background-color: #f8f9fa;
                    width: 250px;
                    transition: width 0.3s;
                    overflow-y: auto;
                    height: calc(100vh - 64px - 50px);
                    position: sticky;
                    top: 64px;
                }

                .sidebar.closed {
                    width: 60px;
                }

                .sidebar ul {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }

                .sidebar li {
                    margin: 0;
                    padding: 0;
                }

                .sidebar li a {
                    display: flex;
                    align-items: center;
                    padding: 1rem;
                    color: #333;
                    text-decoration: none;
                    transition: background-color 0.3s;
                }

                .sidebar li a:hover {
                    background-color: #e9ecef;
                }

                .sidebar li.active a {
                    background-color: #e3f2fd;
                    color: #0070f3;
                    border-left: 3px solid #0070f3;
                }

                .sidebar .material-icons {
                    margin-right: 1rem;
                }

                .sidebar.closed .nav-text {
                    display: none;
                }

                .main-content {
                    flex: 1;
                    padding: 2rem;
                    transition: margin-left 0.3s;
                }

                .main-content.sidebar-open {
                    margin-left: 0;
                }

                .main-content.sidebar-closed {
                    margin-left: 0;
                }

                .footer {
                    background-color: #f8f9fa;
                    padding: 1rem;
                    text-align: center;
                    border-top: 1px solid #e9ecef;
                }

                @media (max-width: 768px) {
                    .sidebar {
                        position: fixed;
                        z-index: 99;
                        height: 100vh;
                        top: 64px;
                    }

                    .sidebar.closed {
                        width: 0;
                    }

                    .main-content {
                        margin-left: 0 !important;
                    }
                }
            `}</style>
        </div>
    );
};

export default Layout;