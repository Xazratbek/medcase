# MedCase Pro Platform - Qidiruv Servisi
# PostgreSQL Full-text search

from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, or_, and_, desc
from sqlalchemy.dialects.postgresql import TSVECTOR

from modellar.holat import Holat
from modellar.kategoriya import AsosiyKategoriya, KichikKategoriya, Bolim
from modellar.foydalanuvchi import Foydalanuvchi


class QidiruvServisi:
    """
    PostgreSQL Full-text search servisi.
    Holatlar, kategoriyalar va foydalanuvchilarni qidirish.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def holatlar_qidirish(
        self,
        qidiruv: str,
        kategoriya_id: UUID = None,
        qiyinlik: str = None,
        teglar: List[str] = None,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[Dict], int]:
        """
        Holatlarni full-text search bilan qidiradi.
        PostgreSQL ts_rank va to_tsvector ishlatadi.
        """
        # Qidiruv so'zlarini tayyorlash
        qidiruv_sozlari = ' & '.join(qidiruv.strip().split())
        
        # Asosiy so'rov
        sorov = text("""
            SELECT 
                h.id,
                h.sarlavha,
                h.tavsif,
                h.qiyinlik,
                h.teglar,
                h.yaratilgan_vaqt,
                k.nomi as kategoriya_nomi,
                ts_rank(
                    to_tsvector('simple', coalesce(h.sarlavha, '') || ' ' || coalesce(h.tavsif, '')),
                    to_tsquery('simple', :qidiruv)
                ) as relevance
            FROM holatlar h
            LEFT JOIN bolimlar b ON h.bolim_id = b.id
            LEFT JOIN kichik_kategoriyalar kk ON b.kichik_kategoriya_id = kk.id
            LEFT JOIN kategoriyalar k ON kk.kategoriya_id = k.id
            WHERE h.faol = true
            AND h.nashr_qilingan = true
            AND (
                to_tsvector('simple', coalesce(h.sarlavha, '') || ' ' || coalesce(h.tavsif, ''))
                @@ to_tsquery('simple', :qidiruv)
                OR h.sarlavha ILIKE :like_qidiruv
                OR h.tavsif ILIKE :like_qidiruv
            )
            ORDER BY relevance DESC, h.yaratilgan_vaqt DESC
            LIMIT :limit OFFSET :offset
        """)
        
        hisob_sorov = text("""
            SELECT COUNT(*)
            FROM holatlar h
            WHERE h.faol = true
            AND h.nashr_qilingan = true
            AND (
                to_tsvector('simple', coalesce(h.sarlavha, '') || ' ' || coalesce(h.tavsif, ''))
                @@ to_tsquery('simple', :qidiruv)
                OR h.sarlavha ILIKE :like_qidiruv
                OR h.tavsif ILIKE :like_qidiruv
            )
        """)
        
        offset = (sahifa - 1) * hajm
        like_qidiruv = f"%{qidiruv}%"
        
        natija = await self.db.execute(
            sorov,
            {
                "qidiruv": qidiruv_sozlari,
                "like_qidiruv": like_qidiruv,
                "limit": hajm,
                "offset": offset
            }
        )
        
        jami_natija = await self.db.execute(
            hisob_sorov,
            {
                "qidiruv": qidiruv_sozlari,
                "like_qidiruv": like_qidiruv
            }
        )
        
        rows = natija.fetchall()
        jami = jami_natija.scalar()
        
        holatlar = []
        for row in rows:
            holatlar.append({
                "id": str(row.id),
                "sarlavha": row.sarlavha,
                "tavsif": row.tavsif[:200] + "..." if row.tavsif and len(row.tavsif) > 200 else row.tavsif,
                "qiyinlik": row.qiyinlik,
                "teglar": row.teglar,
                "kategoriya_nomi": row.kategoriya_nomi,
                "relevance": float(row.relevance) if row.relevance else 0
            })
        
        return holatlar, jami
    
    async def kategoriyalar_qidirish(
        self,
        qidiruv: str,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[Dict], int]:
        """Kategoriyalarni qidiradi."""
        like_qidiruv = f"%{qidiruv.lower()}%"
        
        sorov = select(AsosiyKategoriya).where(
            and_(
                AsosiyKategoriya.faol == True,
                or_(
                    AsosiyKategoriya.nomi.ilike(like_qidiruv),
                    AsosiyKategoriya.tavsif.ilike(like_qidiruv)
                )
            )
        ).order_by(AsosiyKategoriya.nomi)
        
        hisob = select(func.count(AsosiyKategoriya.id)).where(
            and_(
                AsosiyKategoriya.faol == True,
                or_(
                    AsosiyKategoriya.nomi.ilike(like_qidiruv),
                    AsosiyKategoriya.tavsif.ilike(like_qidiruv)
                )
            )
        )
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob)
        
        kategoriyalar = natija.scalars().all()
        
        return [
            {
                "id": str(k.id),
                "nomi": k.nomi,
                "tavsif": k.tavsif,
                "rasm_url": k.rasm_url,
                "rang": k.rang
            }
            for k in kategoriyalar
        ], jami.scalar()
    
    async def foydalanuvchilar_qidirish(
        self,
        qidiruv: str,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[Dict], int]:
        """Foydalanuvchilarni qidiradi (profil ochiq bo'lganlar)."""
        like_qidiruv = f"%{qidiruv.lower()}%"
        
        sorov = text("""
            SELECT 
                f.id,
                f.foydalanuvchi_nomi,
                f.ism,
                f.familiya,
                f.rol,
                p.avatar_url,
                p.muassasa,
                p.profil_ochiq
            FROM foydalanuvchilar f
            LEFT JOIN foydalanuvchi_profillari p ON f.id = p.foydalanuvchi_id
            WHERE f.faol = true
            AND (p.profil_ochiq = true OR p.profil_ochiq IS NULL)
            AND (
                f.foydalanuvchi_nomi ILIKE :qidiruv
                OR f.ism ILIKE :qidiruv
                OR f.familiya ILIKE :qidiruv
                OR CONCAT(f.ism, ' ', f.familiya) ILIKE :qidiruv
            )
            ORDER BY f.ism
            LIMIT :limit OFFSET :offset
        """)
        
        hisob = text("""
            SELECT COUNT(*)
            FROM foydalanuvchilar f
            LEFT JOIN foydalanuvchi_profillari p ON f.id = p.foydalanuvchi_id
            WHERE f.faol = true
            AND (p.profil_ochiq = true OR p.profil_ochiq IS NULL)
            AND (
                f.foydalanuvchi_nomi ILIKE :qidiruv
                OR f.ism ILIKE :qidiruv
                OR f.familiya ILIKE :qidiruv
            )
        """)
        
        offset = (sahifa - 1) * hajm
        
        natija = await self.db.execute(
            sorov,
            {"qidiruv": like_qidiruv, "limit": hajm, "offset": offset}
        )
        jami = await self.db.execute(hisob, {"qidiruv": like_qidiruv})
        
        rows = natija.fetchall()
        
        return [
            {
                "id": str(row.id),
                "foydalanuvchi_nomi": row.foydalanuvchi_nomi,
                "ism": row.ism,
                "familiya": row.familiya,
                "toliq_ism": f"{row.ism} {row.familiya}",
                "rol": row.rol,
                "avatar_url": row.avatar_url,
                "muassasa": row.muassasa
            }
            for row in rows
        ], jami.scalar()
    
    async def umumiy_qidiruv(
        self,
        qidiruv: str,
        har_biridan: int = 5
    ) -> Dict[str, Any]:
        """
        Barcha turlar bo'yicha umumiy qidiruv.
        Holatlar, kategoriyalar va foydalanuvchilarni qaytaradi.
        """
        # Parallel qidiruv
        holatlar, holatlar_jami = await self.holatlar_qidirish(
            qidiruv, sahifa=1, hajm=har_biridan
        )
        kategoriyalar, kategoriyalar_jami = await self.kategoriyalar_qidirish(
            qidiruv, sahifa=1, hajm=har_biridan
        )
        foydalanuvchilar, foydalanuvchilar_jami = await self.foydalanuvchilar_qidirish(
            qidiruv, sahifa=1, hajm=har_biridan
        )
        
        return {
            "holatlar": {
                "natijalar": holatlar,
                "jami": holatlar_jami
            },
            "kategoriyalar": {
                "natijalar": kategoriyalar,
                "jami": kategoriyalar_jami
            },
            "foydalanuvchilar": {
                "natijalar": foydalanuvchilar,
                "jami": foydalanuvchilar_jami
            },
            "jami_topildi": holatlar_jami + kategoriyalar_jami + foydalanuvchilar_jami
        }
    
    async def taklif_qidiruv(
        self,
        qidiruv: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Autocomplete uchun tez qidiruv.
        Faqat sarlavha va nomlarni qaytaradi.
        """
        like_qidiruv = f"{qidiruv.lower()}%"  # Boshidan qidirish - tezroq
        
        sorov = text("""
            (
                SELECT 'holat' as turi, sarlavha as nom, id::text
                FROM holatlar
                WHERE faol = true AND nashr_qilingan = true
                AND LOWER(sarlavha) LIKE :qidiruv
                LIMIT :limit
            )
            UNION ALL
            (
                SELECT 'kategoriya' as turi, nomi as nom, id::text
                FROM kategoriyalar
                WHERE faol = true
                AND LOWER(nomi) LIKE :qidiruv
                LIMIT :limit
            )
            LIMIT :total_limit
        """)
        
        natija = await self.db.execute(
            sorov,
            {"qidiruv": like_qidiruv, "limit": limit // 2, "total_limit": limit}
        )
        
        rows = natija.fetchall()
        
        return [
            {
                "turi": row.turi,
                "nom": row.nom,
                "id": row.id
            }
            for row in rows
        ]
