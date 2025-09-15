import { Avatar } from '../components/Avatar';
import FriendIcon from '@/assets/icons/friend-sidebar.svg';

interface SidebarItemProps {
  Icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  label: string;
  avatar?: string;
}

const SidebarItem = ({ Icon, label, avatar }: SidebarItemProps) => {
  return (
    <li className="flex items-center gap-3 px-4 py-2 hover:bg-gray-100 hover:text-black rounded-lg cursor-pointer">
      {avatar ? (
        <Avatar src={avatar} size="md" />
      ) : Icon ? (
        <Icon className="w-12 h-12 text-gray-700" />
      ) : null}
      <p className="font-medium text-lg">{label}</p>
    </li>
  );
};

export const Sidebar = () => {
  return (
    <aside className="hidden lg:block lg:w-1/4 h-screen">
      <ul className="flex flex-col gap-1 p-2">
        <SidebarItem
          avatar="https://i.pinimg.com/originals/6b/d8/28/6bd828068a62aab41e75ebf829e2fc5d.jpg"
          label="Minsara Vithanage"
        />
        <SidebarItem Icon={FriendIcon} label="Friends" />
      </ul>
    </aside>
  );
};
