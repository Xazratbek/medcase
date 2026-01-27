import { FaTelegram } from 'react-icons/fa';

export default function Footer() {
  return (
    <footer className="py-4 mt-8 text-center text-sm text-gray-500">
      <div className="flex items-center justify-center space-x-2">
        <span>Created by: @Xazratbek</span>
        <a
          href="https://t.me/xazratbek"
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-400 hover:text-white"
        >
          <FaTelegram size={20} />
        </a>
      </div>
    </footer>
  );
}
