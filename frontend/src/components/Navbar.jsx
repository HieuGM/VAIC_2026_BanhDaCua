import React, { useState, useEffect, useRef } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { FaBars, FaTimes, FaChevronDown } from 'react-icons/fa';
import logoImg from '../image/logo.png';
import './Navbar.css';

const navItems = [
  { label: 'Trang chủ', path: '/' },
  {
    label: 'Giới thiệu',
    path: '/about',
    children: [
      { label: 'Giới thiệu chung', path: '/about#intro' },
      { label: 'Ban lãnh đạo', path: '/about#leadership' },
      { label: 'Cơ cấu tổ chức', path: '/about#structure' },
      { label: 'Quá trình phát triển', path: '/about#history' },
    ],
  },
  {
    label: 'Dịch vụ',
    path: '/services',
    children: [
      { label: 'Khoa khám bệnh tự nguyện', path: '/services#voluntary' },
      { label: 'Chăm sóc mạch vành', path: '/services#coronary' },
      { label: 'Khoa dược & hiệu thuốc', path: '/services#pharmacy' },
      { label: 'Khám sức khoẻ', path: '/services#checkup' },
      { label: 'Chăm sóc tại nhà', path: '/services#homecare' },
    ],
  },
  {
    label: 'Hướng dẫn khám bệnh',
    path: '/guide',
    children: [
      { label: 'Quy trình khám chữa bệnh', path: '/guide#process' },
      { label: 'Bảng giá dịch vụ', path: '/guide#pricing' },
      { label: 'Lịch làm việc bác sĩ', path: '/guide#schedule' },
      { label: 'Hướng dẫn đặt lịch', path: '/guide#how-to-book' },
    ],
  },
  { label: 'Đặt lịch khám', path: '/booking', highlight: true },
];

const Navbar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [openDropdown, setOpenDropdown] = useState(null);
  const navRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (navRef.current && !navRef.current.contains(e.target)) {
        setMobileOpen(false);
        setOpenDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const closeMobile = () => {
    setMobileOpen(false);
    setOpenDropdown(null);
  };

  return (
    <header className={`navbar-header ${scrolled ? 'scrolled' : ''}`} ref={navRef}>
      {/* Main Nav */}
      <div className="navbar-main">
        <div className="container navbar-inner">
          {/* Logo */}
          <Link to="/" className="navbar-logo" onClick={closeMobile}>
            <img src={logoImg} alt="Bệnh viện tim Hà Nội" className="logo-image-file" />
            <div className="logo-text">
              <span className="logo-name">Bệnh viện tim Hà Nội</span>
              <span className="logo-slogan">Vì một trái tim khoẻ mạnh</span>
            </div>
          </Link>

          {/* Desktop Nav */}
          <nav className="navbar-links">
            {navItems.map((item) => (
              <div
                key={item.path}
                className="nav-item"
                onMouseEnter={() => item.children && setOpenDropdown(item.path)}
                onMouseLeave={() => setOpenDropdown(null)}
              >
                <NavLink
                  to={item.path}
                  end={item.path === '/'}
                  className={({ isActive }) =>
                    `nav-link ${isActive ? 'active' : ''} ${item.highlight ? 'nav-link-cta' : ''}`
                  }
                >
                  {item.label}
                  {item.children && <FaChevronDown className="nav-chevron" />}
                </NavLink>

                {item.children && (
                  <div className={`dropdown ${openDropdown === item.path ? 'open' : ''}`}>
                    {item.children.map((child) => (
                      <Link
                        key={child.path}
                        to={child.path}
                        className="dropdown-item"
                        onClick={() => setOpenDropdown(null)}
                      >
                        <span className="dropdown-dot" />
                        {child.label}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>

          {/* Mobile Toggle */}
          <button
            className="mobile-toggle"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <FaTimes /> : <FaBars />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <div className={`mobile-menu ${mobileOpen ? 'open' : ''}`}>
        {navItems.map((item) => (
          <div key={item.path} className="mobile-nav-item">
            <div
              className="mobile-nav-header"
              onClick={() =>
                item.children
                  ? setOpenDropdown(openDropdown === item.path ? null : item.path)
                  : null
              }
            >
              <NavLink
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `mobile-nav-link ${isActive ? 'active' : ''} ${item.highlight ? 'cta' : ''}`
                }
                onClick={item.children ? (e) => e.preventDefault() : closeMobile}
              >
                {item.label}
              </NavLink>
              {item.children && (
                <FaChevronDown
                  className={`mobile-chevron ${openDropdown === item.path ? 'open' : ''}`}
                />
              )}
            </div>

            {item.children && openDropdown === item.path && (
              <div className="mobile-dropdown">
                {item.children.map((child) => (
                  <Link
                    key={child.path}
                    to={child.path}
                    className="mobile-dropdown-item"
                    onClick={closeMobile}
                  >
                    {child.label}
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </header>
  );
};

export default Navbar;
