import React from 'react';
import { Link } from 'react-router-dom';
import { Scan, Menu, X } from 'lucide-react';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';

export const Navbar = () => {
  const [isScrolled, setIsScrolled] = React.useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  React.useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300 border-b',
        isScrolled
          ? 'bg-base-900/80 backdrop-blur-md border-base-700/50 py-3 shadow-lg'
          : 'bg-transparent border-transparent py-5'
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="p-2 bg-primary/10 rounded-xl group-hover:bg-primary/20 transition-colors">
              <Scan className="w-6 h-6 text-primary" />
            </div>
            <span className="font-bold text-xl tracking-tight text-white">
              AI Product <span className="text-primary">Analyzer</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-6">
            <Link to="/history" className="text-text-secondary hover:text-white font-medium transition-colors">
              History
            </Link>
            <Link to="/scan">
              <Button size="sm">New Scan</Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 text-text-secondary hover:text-white"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      {isMobileMenuOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-base-900 border-b border-base-700/50 py-4 px-4 shadow-xl">
          <div className="flex flex-col gap-4">
            <Link
              to="/history"
              className="text-text-secondary hover:text-white font-medium p-2"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              History
            </Link>
            <Link to="/scan" onClick={() => setIsMobileMenuOpen(false)}>
              <Button className="w-full">New Scan</Button>
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
};
