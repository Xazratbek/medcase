# MedCase Pro Platform - Sarlavha Tozalash Skripti
# Mavjud bazadagi [id] prefikslarini olib tashlash

import asyncio
import re
import sys
import os

# Loyiha ildizini Python path ga qo'shish
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from sozlamalar.malumotlar_bazasi import async_sessiya_yaratuvchi
from modellar.holat import Holat


async def sarlavhalarni_tozalash():
    """
    Barcha holatlarning sarlavhalaridan [xxx_xxx] formatidagi 
    prefikslarni olib tashlaydi va birinchi harfni katta qiladi.
    """
    async with async_sessiya_yaratuvchi() as db:
        # Barcha holatlarni olish
        sorov = select(Holat)
        natija = await db.execute(sorov)
        holatlar = natija.scalars().all()
        
        yangilangan = 0
        pattern = re.compile(r'^\[[\w_]+\]\s*')
        
        for holat in holatlar:
            yangi_sarlavha = holat.sarlavha
            
            # [xxx_xxx] formatidagi prefiksni olib tashlash
            if pattern.match(yangi_sarlavha):
                yangi_sarlavha = pattern.sub('', yangi_sarlavha)
            
            # Birinchi harfni katta qilish
            if yangi_sarlavha and yangi_sarlavha[0].islower():
                yangi_sarlavha = yangi_sarlavha[0].upper() + yangi_sarlavha[1:]
            
            # Agar o'zgarish bo'lsa, yangilash
            if yangi_sarlavha != holat.sarlavha:
                holat.sarlavha = yangi_sarlavha
                yangilangan += 1
        
        await db.commit()
        print(f"Jami {yangilangan} ta holat sarlavhasi yangilandi.")
        return yangilangan


if __name__ == "__main__":
    asyncio.run(sarlavhalarni_tozalash())
