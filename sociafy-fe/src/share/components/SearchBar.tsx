'use client';
import SearchIcon from '@/assets/icons/search.svg';

export const SearchBar = () => {
  return (
    <div className="flex items-center bg-gray-700 px-3 py-1.5 rounded-full w-60">
      <SearchIcon alt="Search" className="w-4 h-4 opacity-70" />
      <input
        type="text"
        placeholder="Search Facebook"
        className="ml-2 flex-1 border-none outline-none bg-transparent text-sm text-white placeholder-gray-400"
      />
    </div>
  );
};
