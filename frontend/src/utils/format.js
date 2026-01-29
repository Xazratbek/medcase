export const formatQiyinlik = (value) => {
  if (!value) return '';
  const raw = String(value).toLowerCase().trim();
  const key = raw.replace(/[^a-z]/g, '');

  if (key === 'oson') return 'Oson';
  if (key === 'ortacha' || key === 'orta') return "O'rtacha";
  if (key === 'qiyin') return 'Qiyin';

  return value;
};
