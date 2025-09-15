'use client';
import Image from 'next/image';
import HomeIcon from '@/assets/icons/home-header.svg';
import VideoIcon from '@/assets/icons/video-header.svg';
import NotifyIcon from '@/assets/icons/notify-header.svg';
import Logo from '@/assets/images/logo.png';
import { Avatar } from '../components/Avatar';
import { SearchBar } from '../components/SearchBar';

export const Header = () => {
  return (
    <header className="flex justify-between items-center py-2 px-6 border-b border-gray-300 bg-[#1c1e21] shadow-lg">
      {/* Left */}
      <div className="flex items-center gap-2 flex-1">
        <Image src={Logo || ''} alt="Logo" width={40} height={40} />
        <SearchBar />
      </div>

      {/* Middle - Navbar */}
      <nav className="hidden sm:flex justify-center gap-4">
        {[HomeIcon, VideoIcon].map((Icon, idx) => (
          <button
            key={idx}
            className="
        md:px-10 md:py-3 md:rounded-md 
        hover:bg-gray-600 focus:bg-blue-500 focus:outline-none transition-colors
        px-3 py-3 rounded-full
      "
          >
            <Icon className="w-7 h-7 text-gray-300" />
          </button>
        ))}
      </nav>

      {/* Right */}
      <div className="flex items-center gap-3 flex-1 justify-end">
        <button className="p-3 bg-gray-700 rounded-full hover:bg-gray-600 transition-colors">
          <NotifyIcon className="w-5 h-5 text-white" />
        </button>
        <Avatar src="https://i.pinimg.com/originals/6b/d8/28/6bd828068a62aab41e75ebf829e2fc5d.jpg" />
      </div>
    </header>
  );
};
