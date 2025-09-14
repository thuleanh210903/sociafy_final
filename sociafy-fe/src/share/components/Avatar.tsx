import { Camera } from 'lucide-react';

interface AvatarProps {
  src: string;
  alt?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  isOnline?: boolean;
  isMe?: boolean;
  onUploadClick?: () => void;
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt = 'avatar',
  size = 'md',
  className = '',
  isOnline = false,
  isMe = false,
  onUploadClick,
}) => {
  const sizeClass = {
    sm: 'w-6 h-6 lg:w-8 lg:h-8', // comment
    md: 'w-10 h-10 lg:w-12 lg:h-12', // post
    lg: 'w-24 h-24 md:w-32 md:h-32 lg:w-40 lg:h-40', // profile
  };

  const uploadBtnSize = {
    sm: 'w-4 h-4 text-[10px]',
    md: 'w-5 h-5 text-xs',
    lg: 'w-10 h-10 text-md',
  };

  return (
    <div className={`inline-block relative ${sizeClass[size]} ${className}`}>
      <img
        src={src}
        alt={alt}
        className="w-full h-full rounded-full object-cover border"
      />

      {/* Online indicator */}
      {isOnline && (
        <span
          className={`absolute bottom-0 right-0 block rounded-full border-2 border-white 
            ${size === 'lg' ? 'w-5 h-5' : 'w-2.5 h-2.5'} bg-green-500`}
        />
      )}

      {/* Upload button */}
      {isMe && (
        <button
          onClick={onUploadClick}
          className={`absolute bottom-0 right-0 flex items-center justify-center rounded-full bg-white/80 text-gray-800 shadow-md hover:bg-white transition ${uploadBtnSize[size]}`}
        >
          <Camera size={14} />
        </button>
      )}
    </div>
  );
};
